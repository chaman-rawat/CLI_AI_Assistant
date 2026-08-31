import argparse
import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI, OpenAIError, RateLimitError
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

if not base_url:
    raise RuntimeError("OPENROUTER_BASE_URL is not set")

client = OpenAI(base_url=base_url, api_key=api_key)

model = os.getenv("MODEL_NAME", "gpt-4o-mini")

DEFAULT_SYSTEM_PROMPT = "You are a helpful Assistant. Be concise."
HISTORY_FILE = "history.json"


class TextSummary(BaseModel):
    main_topic: str
    key_entities: list[str]
    sentiment: Literal["positive", "neutral", "negative"]
    one_line_summary: str


def clear_history():
    user_input = input("Are you sure you want clear history (Y/N): ")
    if user_input.strip().lower() in ["y", "yes"]:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            print("History deleted successfully.")
        else:
            print("History does not exist.")
    else:
        print("Skipping clearing history.")


def extract_structured_output(text):
    try:
        response = client.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": ("Extract structured information from the given text."),
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            response_format=TextSummary,
        )

        parsed_output = response.choices[0].message.parsed
        print("Main topic:", parsed_output.main_topic)
        print("Key entities:", parsed_output.key_entities)
        print("Sentiment:", parsed_output.sentiment)
        print("One line summary:", parsed_output.one_line_summary)

    except AuthenticationError:
        print("Error: invalid API key. Check your .env file.")
    except RateLimitError:
        print("Error: rate limit hit. Wait a moment and try again.")
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")


def one_shot(prompt, system_instruction):
    system_prompt = {
        "role": "system",
        "content": system_instruction,
    }

    try:
        # Send User query with system prompt to API.
        response = client.chat.completions.create(
            model=model,
            messages=[system_prompt, {"role": "user", "content": prompt}],
        )

        # Assistant reply
        reply = response.choices[0].message.content

        print(f"\nAssistant: {reply}\n")

    except AuthenticationError:
        print("Error: invalid API key. Check your .env file.")
    except RateLimitError:
        print("Error: rate limit hit. Wait a moment and try again.")
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")


def start_repl(system_instruction):
    system_prompt = {
        "role": "system",
        "content": system_instruction,
    }

    # Load messages history
    messages = []
    try:
        with open(HISTORY_FILE, "r") as file:
            messages = json.load(file)
            print("Previous history loaded from the history.json file...")
    except FileNotFoundError:
        print("No saved history found...")
    except json.JSONDecodeError:
        print(
            "Error: The history.json file is not a valid JSON document. Continuing with no history."
        )

    print("REPL mode started. Type 'quit' or 'exit' to end.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break
        elif not user_input:
            continue

        # Append the user's message to history.
        messages.append({"role": "user", "content": user_input})

        try:
            # Send the full history to the API.
            response = client.chat.completions.create(
                model=model,
                messages=[system_prompt] + messages[-40:],
            )

            # Append the model's reply to history.
            reply = response.choices[0].message.content

            messages.append({"role": "assistant", "content": reply})

            print(f"\nAssistant: {reply}\n")

            # Update history with new messages
            with open(HISTORY_FILE, "w") as file:
                json.dump(messages, file, indent=4)

        except AuthenticationError:
            messages.pop()
            print("Error: invalid API key. Check your .env file.")
        except RateLimitError:
            messages.pop()
            print("Error: rate limit hit. Wait a moment and try again.")
        except OpenAIError as e:
            messages.pop()
            print(f"OpenAI API error: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI AI Assistant")

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to the assistant",
    )

    parser.add_argument(
        "--system",
        help="Override the default system prompt",
    )

    parser.add_argument(
        "--structured",
        action="store_true",
        help="Use structured extraction mode",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear conversation history and exit",
    )

    args = parser.parse_args()

    # Clear mode
    if args.clear:
        clear_history()
        return

    # Only strip prompt if one was actually provided
    if args.prompt is not None:
        args.prompt = args.prompt.strip()

        if not args.prompt:
            parser.error("prompt cannot be empty or whitespace only")

    # Structured extraction mode
    if args.structured:
        if args.prompt is None:
            parser.error("--structured requires a prompt")
        extract_structured_output(args.prompt)
        return

    # Decide which system prompt to use
    system_instruction = args.system or DEFAULT_SYSTEM_PROMPT

    # One-shot mode
    if args.prompt:
        one_shot(args.prompt, system_instruction)
        return

    # REPL mode
    start_repl(system_instruction)


if __name__ == "__main__":
    main()
