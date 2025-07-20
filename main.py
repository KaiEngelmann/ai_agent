import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse

def main():

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set in environment")


    client = genai.Client(api_key=api_key)

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
        model="gemini-2.0-flash-001", 
        contents=messages
    )

    if response.candidates and response.candidates[0].content.parts:
        reply = response.candidates[0].content.parts[0].text
    else:
        reply = "No response recieved"

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

