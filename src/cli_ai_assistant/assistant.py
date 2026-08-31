import argparse
import json
import os

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI, OpenAIError, RateLimitError

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"), api_key=os.getenv("OPENROUTER_API_KEY")
)

model = os.getenv("MODEL_NAME")

DEFAULT_SYSTEM_PROMPT = "You are a helpful Assistant. Be concise."
HISTORY_FILE = "history.json"


def clear_history():
    user_input = input("Are you sure you want clear history (Y/N): ")
    if user_input.strip().lower() in ["y", "yes"]:
        with open(HISTORY_FILE, "w") as file:
            json.dump([], file)
            print("History successfully cleared!")
    else:
        print("Skipping clearing history.")


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
                messages=[system_prompt] + messages,
            )

            # Append the model's reply to history.
            reply = response.choices[0].message.content

            messages.append({"role": "assistant", "content": reply})

            print(f"\nAssistant: {reply}\n")

            # Update history with new messages
            with open(HISTORY_FILE, "w") as file:
                json.dump(messages, file, indent=4)

        except AuthenticationError:
            print("Error: invalid API key. Check your .env file.")
        except RateLimitError:
            print("Error: rate limit hit. Wait a moment and try again.")
        except OpenAIError as e:
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
        print("Chosen Clear mode")
        clear_history()
        return

    # Structured extraction mode
    if args.structured:
        if not args.prompt:
            parser.error("--structured requires a prompt")

        print("Chosen Structured output")
        print("Prompt:", args.prompt)
        return

    # Decide which system prompt to use
    if args.system:
        print("Custom system prompt:", args.system)

    system_instruction = args.system or DEFAULT_SYSTEM_PROMPT

    # One-shot mode
    if args.prompt:
        print("Chosen One-Shot mode")
        print("Prompt:", args.prompt)
        one_shot(args.prompt, system_instruction)
        return

    # REPL mode
    print("Chosen REPL mode")
    start_repl(system_instruction)


if __name__ == "__main__":
    main()
