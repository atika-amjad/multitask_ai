from __future__ import annotations

import sys
from pathlib import Path

# Allow running as: python agent/main.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent import Agent  # noqa: E402

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


def main() -> None:
    workspace = PROJECT_ROOT
    agent = Agent(workspace_root=workspace)

    print("Multitask AI Agent (Ollama Cloud)")
    print(f"Model: {agent.model}")
    print("Tools: calculator, compose, web_search, email, filesystem")
    print("Commands: /clear (reset memory), /quit (exit)")
    print(f"Workspace: {workspace}\n")

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"/quit", "/exit", "quit", "exit"}:
            print("Goodbye.")
            break
        if user_input.lower() == "/clear":
            agent.memory.clear()
            print("Conversation memory cleared.")
            continue

        try:
            reply = agent.handle(user_input)
        except EnvironmentError as exc:
            print(f"Setup error: {exc}")
            print("Set OLLAMA_API_KEY (and SMTP_* for email) then try again.")
            continue
        except Exception as exc:
            print(f"Error: {exc}")
            continue

        print(f"\nAgent> {reply}\n")


if __name__ == "__main__":
    main()
