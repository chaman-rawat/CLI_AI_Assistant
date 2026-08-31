# CLI AI Assistant

A lightweight command-line AI assistant.

## Prerequisites

- Python 3.14+
- `uv` installed
- An API key for either OpenRouter or an OpenAI-compatible provider

## Setup

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your values.

   ```env
   OPENROUTER_API_KEY=your-api-key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   MODEL_NAME=gpt-4o-mini
   ```

   Change the base URL for providers other than OpenRouter.

3. Install the project dependencies with `uv`:

   ```bash
   uv sync
   ```

## Run the project

To see the CLI usage and available options:

```bash
uv run assistant.py --help
```

## Example usage

### Interactive REPL mode

```bash
uv run assistant.py
```

Starts a chat session in the terminal. The assistant keeps conversation history in `history.json` and reloads it the next time you start the REPL. Type `quit` or `exit` to leave.

### One-shot prompt

```bash
uv run assistant.py "What is the speed of light?"
```

Sends a single prompt and exits after printing the response.

### Custom system prompt

```bash
uv run assistant.py --system "You are a Python code reviewer. Be terse." "Explain this function in plain English"
```

Overrides the default assistant persona for the session.

### Structured extraction mode

```bash
uv run assistant.py --structured "Tesla launched a new affordable electric car. Customers reacted positively, praising its price and range."
```

Extracts a structured summary with fields like `main_topic`, `key_entities`, `sentiment`, and `one_line_summary`.

### Clear history

```bash
uv run assistant.py --clear
```

Deletes the saved `history.json` file after confirmation.

## Notes

- The project expects the environment variables from `.env` to be available at runtime.
- `history.json` is used to store chat history in the project root while the REPL is running.
