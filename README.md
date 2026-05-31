# Multitask AI Agent

A command-line AI assistant powered by [Ollama Cloud](https://ollama.com/cloud). It routes user requests to the right tools, runs multi-step workflows (search → save → email, or compose → email), and keeps conversation memory.

## Features

- **Ollama Cloud** — Uses your Ollama API key and cloud models (e.g. `gemma3:12b`, `gpt-oss:120b`)
- **Multi-step plans** — Chains tools automatically (e.g. web search, write file, send email)
- **Tools**
  - `calculator` — Safe math evaluation
  - `compose` — Generates documents (diet plans, letters, guides)
  - `web_search` — DuckDuckGo search via the `ddgs` package
  - `filesystem` — Read, write, and list files (sandboxed to the project workspace)
  - `email` — SMTP email with HTML + plain text (Gmail-compatible)
- **Conversation memory** — Context across turns in the same session

## Project structure

```
multitask_ai/
├── agent/
│   ├── main.py              # CLI entry point
│   ├── agent.py             # Planner, tool execution, orchestration
│   ├── tools/
│   │   ├── calculator.py
│   │   ├── web_search.py
│   │   ├── email.py
│   │   └── filesystem.py
│   ├── memory/
│   │   └── conversation.py
│   └── prompts/
│       └── router.txt       # Task planner instructions
├── requirements.txt
├── .env.example             # Copy to .env and fill in secrets
└── README.md
```

## Requirements

- Python 3.10+
- [Ollama Cloud API key](https://ollama.com/settings/keys)
- SMTP credentials (only if you use the email tool)

## Setup

1. **Clone or open the project** and create a virtual environment:

   ```powershell
   cd multitask_ai
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**

   ```powershell
   copy .env.example .env
   ```

   Edit `.env`:

   | Variable | Description |
   |----------|-------------|
   | `OLLAMA_API_KEY` | Ollama Cloud API key |
   | `OLLAMA_HOST` | `https://ollama.com` |
   | `OLLAMA_MODEL` | Model name from [ollama.com/api/tags](https://ollama.com/api/tags) |
   | `SMTP_*` | Required for email (Gmail: use an [app password](https://support.google.com/accounts/answer/185833)) |
   | `SMTP_SENDER_NAME` | Display name in the From header (e.g. `Atika Amjad`) |

3. **Run the agent:**

   ```powershell
   python agent/main.py
   ```

## Usage examples

**Chat only** — general questions with no tools.

**Calculator**

```text
What is 15% of 840?
```

**Web search + save + email**

```text
search for latest news of "China", save to china_news.txt, and email to someone@example.com
```

**Compose + email** (AI writes the content — no web search)

```text
make a 30 day diet plan to gain weight and send email to someone@example.com with regards "Your Name"
```

**CLI commands**

| Command | Action |
|---------|--------|
| `/clear` | Reset conversation memory |
| `/quit` | Exit |

## How it works

1. **Plan** — The router (LLM + `router.txt`) returns a JSON plan: ordered tool steps or a direct reply.
2. **Execute** — Each step runs in order; outputs can flow to the next step (`use_result_from`, `use_file_from_step`).
3. **Summarize** — A final LLM pass describes what was actually done (files written, emails sent).

Creative tasks (plans, letters) use **`compose`** instead of **`web_search`**. News and live facts use **`web_search`**.

## Security notes

- Never commit `.env` — it contains API keys and SMTP passwords.
- The filesystem tool cannot access paths outside the project workspace.
- Revoke and rotate keys if they are ever exposed.

## License

Private project — add a license if you plan to share or publish it.
