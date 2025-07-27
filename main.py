import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse
from functions.get_files_info import schema_get_files_info

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
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )
    
    reply = "No response received"
    function_call_part = None
    text_reply = None
    
    if response.candidates and response.candidates[0].content.parts:
        parts = response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, "function_call") and not function_call_part:
                function_call_part = part.function_call
            elif hasattr(part, "text") and not text_reply:
                text_reply = part.text
        if function_call_part:
            call_info = f"Calling function: {function_call_part.name}({function_call_part.args})"
            reply = f"{call_info}\n\n{text_reply or '[No text reply provided]'}"
        else:
            reply =  text_reply or "No text response"

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

