import argparse
import os

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI, OpenAIError, RateLimitError

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"), api_key=os.getenv("OPENROUTER_API_KEY")
)

system_prompt = {
    "role": "system",
    "content": "You are a helpful Assistant. Be concise.",
}
model = os.getenv("MODEL_NAME")


def start_repl():
    print("REPL mode started. Type 'quit' or 'exit' to end.\n")

    # Load messages history
    messages = []

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

    # One-shot mode
    if args.prompt:
        print("Chosen One-Shot mode")
        print("Prompt:", args.prompt)
        return

    # REPL mode
    print("Chosen REPL mode")


if __name__ == "__main__":
    main()
