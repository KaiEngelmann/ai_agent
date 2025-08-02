import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function



def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set in environment")


    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.0-flash-001"
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file
        ]
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("prompt", nargs= "*", help="User prompt")
    args = parser.parse_args()

    if args.prompt:
        user_prompt = " ".join(args.prompt).strip()
        verbose = args.verbose
    else:
        user_prompt = input("Ask a question: ").strip()
        if "--verbose" in user_prompt:
            verbose = True
            user_prompt = user_prompt.replace("--verbose", "").strip()
        else:
            verbose = False
        if not user_prompt:
            raise Exception ("You must ask a question")

    messages = [
        types.Content(role="user",parts=[types.Part(text=user_prompt)]),
    ]
    
    MAX_ITERATIONS = 20
    reply = None
    
    for step in range(MAX_ITERATIONS):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                )
            )


            for candidate in response.candidates:
                messages.append(candidate.content)

            
            reply = ""
            function_call_part = None
            text_reply = None
            has_function_calls = False
            
            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                for part in parts:
                    if hasattr(part, "function_call"): 
                        has_function_calls = True
                        if not function_call_part:
                            function_call_part = part.function_call
                    elif hasattr(part, "text") and not text_reply:
                        text_reply = part.text

                    
                
                if has_function_calls and function_call_part:
                    function_call_result = call_function(function_call_part, verbose=verbose)
                    try:
                        func_response = function_call_result.parts[0].function_response.response
                    except (AttributeError, IndexError):
                        raise Exception("Function call result is malformed or missing a response")
                    if not func_response:
                        raise Exception("Function call missing response")
                    if verbose:
                        print(f"-> {func_response}\n{text_reply}" if text_reply else str(func_response))
                    messages.append(
                        types.Content(
                            role="tool",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_call_part.name,
                                        response=func_response,
                                    )
                                )
                            ]
                        )
                    )


                response_text = response.text if hasattr(response, 'text') else None
                if response_text and response_text.strip():
                    reply = response_text
                    break

                elif not function_call_part and not text_reply:
                    reply = "No text or function call in response"
                    break
        except Exception as e:
            print(f"Error: {e}")
            print(f"Final response:\n{reply}")
            break
    
    else:
        print("Max iterations reached without final response")

        


    usage = response.usage_metadata
    
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {usage.prompt_token_count}")
        print(f"Response tokens: {usage.candidates_token_count}")
        print(reply)
    else:
        print(reply)

if __name__ == "__main__":

    main()

