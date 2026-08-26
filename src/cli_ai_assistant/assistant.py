import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"), api_key=os.getenv("OPENROUTER_API_KEY")
)

system_prompt = {"role": "system", "content": "You are a helpful Assistant."}
messages = []


def start_repl():
    pass


def main():
    print("Hello from assistant!")


if __name__ == "__main__":
    main()
