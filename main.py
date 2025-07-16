import os
from dotenv import load_dotenv
from google import genai
import sys

def main():

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")


    client = genai.Client(api_key=api_key)

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Ask a question: ").strip()
        if not question:
            raise Exception ("You must ask a question")
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents=question
    )

    usage = response.usage_metadata

    print(response.text)
    print("Prompt tokens:", usage.prompt_token_count)
    print("Response tokens:", usage.candidates_token_count)

if __name__ == "__main__":
    main()

