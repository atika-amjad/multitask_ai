from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from agent.memory.conversation import ConversationMemory
from agent.tools import (
    FilesystemTool,
    calculate,
    format_results,
    send_email,
    web_search,
)

AGENT_DIR = Path(__file__).resolve().parent
ROUTER_PROMPT_PATH = AGENT_DIR / "prompts" / "router.txt"


class Agent:
    def __init__(
        self,
        workspace_root: Path | None = None,
        model: str | None = None,
        memory: ConversationMemory | None = None,
    ):
        self.memory = memory or ConversationMemory()
        self.filesystem = FilesystemTool(workspace_root or Path.cwd())
        self.model = model or os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "https://ollama.com")
        self.router_prompt = ROUTER_PROMPT_PATH.read_text(encoding="utf-8")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from ollama import Client
            except ImportError as exc:
                raise ImportError(
                    "ollama package is required. Install with: pip install ollama"
                ) from exc
            api_key = os.getenv("OLLAMA_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "OLLAMA_API_KEY environment variable is not set. "
                    "Create one at https://ollama.com/settings/keys"
                )
            self._client = Client(
                host=self.ollama_host,
                headers={"Authorization": f"Bearer {api_key}"},
            )
        return self._client

    def _chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str:
        client = self._get_client()
        try:
            response = client.chat(
                model=self.model,
                messages=messages,
                stream=False,
                format="json" if json_mode else None,
                options={"temperature": temperature},
            )
        except Exception as exc:
            err = str(exc).lower()
            if "not found" in err or "404" in err:
                raise ValueError(
                    f"Model '{self.model}' is not available on Ollama Cloud. "
                    f"Set OLLAMA_MODEL to a name from https://ollama.com/api/tags "
                    f"(e.g. gemma3:12b, gpt-oss:120b). "
                    f"Local-only names like 'gemma3:cloud' do not work with the cloud API."
                ) from exc
            raise
        return response.message.content or ""

    def _parse_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if fence:
            text = fence.group(1)
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"Expected JSON, got: {text[:300]}")
        return json.loads(text[start : end + 1])

    def _normalize_plan(self, decision: dict[str, Any]) -> dict[str, Any]:
        # Legacy single-tool format
        if decision.get("use_tool"):
            return {
                "use_tools": True,
                "steps": [
                    {
                        "tool": decision.get("tool", ""),
                        "args": decision.get("args") or {},
                    }
                ],
            }
        if decision.get("use_tools"):
            steps = decision.get("steps") or []
            if not isinstance(steps, list) or not steps:
                raise ValueError("Plan has use_tools=true but no steps")
            return {"use_tools": True, "steps": steps}
        return {"use_tools": False, "reason": decision.get("reason", "")}

    def _wants_email(self, text: str) -> bool:
        if not re.search(r"\b(send|email|e-mail|mail)\b", text, re.I):
            return False
        if self._extract_email(text):
            return True
        return bool(re.search(r"\bsend\s+(?:it\s+)?to\b", text, re.I))

    def _is_factual_question(self, text: str) -> bool:
        if self._wants_email(text):
            return False
        if re.search(r"\b(create|make|write|draft|compose)\b", text, re.I):
            return False
        return bool(
            re.match(
                r"^(what|who|when|where|why|how|which|is|are|does|do|can|could|tell me)\b",
                text.strip(),
                re.I,
            )
        )

    def _step_tool(self, step: dict[str, Any]) -> str:
        tool, _ = self._normalize_tool_name(str(step.get("tool", "")), {})
        return tool

    def _sanitize_plan(
        self, user_message: str, steps: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not steps:
            return steps

        wants_email = self._wants_email(user_message)
        sanitized: list[dict[str, Any]] = []
        for step in steps:
            tool = self._step_tool(step)
            if tool == "email" and not wants_email:
                continue
            sanitized.append(step)

        if self._is_factual_question(user_message):
            search_only = [s for s in sanitized if self._step_tool(s) == "web_search"]
            if search_only:
                return search_only[:1]
            return [
                {
                    "tool": "web_search",
                    "args": {"query": user_message, "max_results": 5},
                }
            ]

        if wants_email and not self._extract_email(user_message):
            sanitized = [s for s in sanitized if self._step_tool(s) != "email"]

        return sanitized

    def _plan_override(self, user_message: str) -> dict[str, Any] | None:
        if self._is_factual_question(user_message):
            return {
                "use_tools": True,
                "steps": [
                    {
                        "tool": "web_search",
                        "args": {"query": user_message, "max_results": 5},
                    }
                ],
            }
        return None

    def plan(self, user_message: str) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": self.router_prompt},
            {
                "role": "user",
                "content": (
                    "Plan for THIS request only. Do not add email unless this message "
                    f"explicitly asks to send/email.\n\n{user_message}"
                ),
            },
        ]
        raw = self._chat(messages, temperature=0.0, json_mode=True)
        return self._normalize_plan(self._parse_json(raw))

    def _normalize_tool_name(self, tool: str, args: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        raw = tool.strip().lower().replace("-", " ")
        aliases = {
            "filesystem write": "filesystem",
            "filesystem read": "filesystem",
            "filesystem list": "filesystem",
            "filesystem_write": "filesystem",
            "filesystem_read": "filesystem",
            "filesystem_list": "filesystem",
            "file": "filesystem",
            "search": "web_search",
            "web": "web_search",
            "mail": "email",
            "calc": "calculator",
            "generate": "compose",
            "draft": "compose",
        }
        if raw in aliases:
            tool = aliases[raw]
        elif raw.startswith("filesystem"):
            tool = "filesystem"
        else:
            tool = raw.replace(" ", "_")

        if tool == "filesystem" and not args.get("action"):
            if "write" in raw:
                args = {**args, "action": "write"}
            elif "read" in raw:
                args = {**args, "action": "read"}
            elif "list" in raw:
                args = {**args, "action": "list"}
            else:
                args = {**args, "action": "write"}

        return tool, args

    def _extract_email(self, text: str) -> str:
        match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
        return match.group(0) if match else ""

    def _extract_regards(self, text: str) -> str:
        match = re.search(
            r'regards\s*["\']?\s*([^"\'"\n]+?)["\']?(?:\s*$|\s+don)',
            text,
            re.I,
        )
        if match:
            return match.group(1).strip()
        return os.getenv("SMTP_SENDER_NAME", "").strip()

    def _is_creative_task(self, text: str) -> bool:
        patterns = [
            r"\b(make|create|write|draft|prepare|design)\b.*\b(plan|letter|guide|schedule|program|menu|diet)\b",
            r"\b\d+\s*days?\s+.*\bplan\b",
            r"\bdiet\s+plan\b",
            r"\bmeal\s+plan\b",
        ]
        return any(re.search(p, text, re.I) for p in patterns)

    def _needs_web_search(self, text: str) -> bool:
        return bool(
            re.search(
                r"\b(search|latest\s+news|look\s+up|find\s+online|current\s+events)\b",
                text,
                re.I,
            )
        )

    def _slug_from_message(self, user_message: str) -> str:
        cleaned = re.sub(r"don'?t\s+forget[^.]*", "", user_message, flags=re.I)
        cleaned = re.sub(r"send\s+email\s+to\s+\S+@\S+", "", cleaned, flags=re.I)
        cleaned = re.sub(r'regards\s*["\']?[^"\']+["\']?', "", cleaned, flags=re.I)
        match = re.search(
            r"(?:make|create|write)\s+(?:a\s+)?(.+?)(?:\s+and\s+|\s*$)",
            cleaned,
            re.I,
        )
        slug = match.group(1).strip() if match else ""
        if not slug and re.search(r"diet\s+plan", cleaned, re.I):
            slug = "30_day_diet_plan_to_gain_weight"
        slug = re.sub(r"[^\w\-]+", "_", (slug or "document").lower()).strip("_")[:50]
        return slug or "document"

    def _subject_from_message(self, user_message: str) -> str:
        if re.search(r"diet\s+plan", user_message, re.I):
            return "30 Day Diet Plan to Gain Weight"
        match = re.search(
            r"(?:make|create|write)\s+(?:a\s+)?(.+?)(?:\s+and\s+|\s+to\s+|\s*$)",
            user_message,
            re.I,
        )
        if match:
            title = match.group(1).strip().rstrip(".")
            return title[:1].upper() + title[1:]
        quoted = re.search(r'["\']([^"\']+)["\']', user_message)
        if quoted:
            return f"Latest News on {quoted.group(1)}"
        return "Message from Atika Amjad"

    def _clean_task_prompt(self, user_message: str) -> str:
        task = re.sub(r"send\s+email\s+to\s+\S+@\S+", "", user_message, flags=re.I)
        task = re.sub(r"don'?t\s+forget[^.]*", "", task, flags=re.I)
        task = re.sub(r'regards\s*["\']?[^"\']+["\']?', "", task, flags=re.I)
        return task.strip()

    def _build_compose_plan(self, user_message: str) -> list[dict[str, Any]]:
        to = self._extract_email(user_message)
        regards = self._extract_regards(user_message)
        task = self._clean_task_prompt(user_message)
        subject = self._subject_from_message(user_message)

        steps: list[dict[str, Any]] = [
            {
                "tool": "compose",
                "args": {"task": task, "regards": regards},
            }
        ]
        if re.search(r"\b(save|file|write\s+to)\b", user_message, re.I):
            steps.append(
                {
                    "tool": "filesystem",
                    "args": {
                        "action": "write",
                        "path": f"{self._slug_from_message(user_message)}.txt",
                    },
                    "use_result_from": 0,
                }
            )
        if to:
            email_step: dict[str, Any] = {
                "tool": "email",
                "args": {
                    "to": to,
                    "subject": subject,
                    "sender_name": regards or None,
                },
            }
            if len(steps) == 2:
                email_step["use_file_from_step"] = 1
            else:
                email_step["use_result_from"] = 0
            steps.append(email_step)
        return steps

    def _fix_plan(self, user_message: str, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._is_creative_task(user_message) or self._needs_web_search(user_message):
            return steps
        tools = []
        for step in steps:
            tool, _ = self._normalize_tool_name(str(step.get("tool", "")), {})
            tools.append(tool)
        if "web_search" in tools or "compose" not in tools:
            return self._build_compose_plan(user_message)
        return steps

    def compose_content(self, task: str, regards: str = "") -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You write complete, practical, well-structured documents. "
                    "Output ONLY the document content — no preamble, no 'here is your plan'. "
                    "Use clear headings, day-by-day breakdowns when asked, and bullet lists where helpful."
                ),
            },
            {"role": "user", "content": task},
        ]
        content = self._chat(messages, temperature=0.5).strip()
        if regards and regards.lower() not in content.lower():
            content += f"\n\nRegards,\n{regards}"
        return content

    def _default_write_path(self, user_message: str, completed: list[dict[str, Any]]) -> str:
        if "news" in user_message.lower():
            for item in completed:
                if item.get("tool") == "web_search":
                    query = str(item.get("args", {}).get("query", ""))
                    slug = re.sub(r"[^\w\-]+", "_", query.lower())[:40] or "news"
                    return f"{slug}_news.txt"
            return "news.txt"
        return f"{self._slug_from_message(user_message)}.txt"

    def _auto_link_steps(
        self, steps: list[dict[str, Any]], user_message: str
    ) -> list[dict[str, Any]]:
        linked: list[dict[str, Any]] = []
        for i, step in enumerate(steps):
            step = dict(step)
            tool, args = self._normalize_tool_name(
                str(step.get("tool", "")), dict(step.get("args") or {})
            )
            if tool == "filesystem" and args.get("action") == "write":
                path = str(args.get("path", "")).strip()
                if not path or path == ".":
                    args["path"] = self._default_write_path(user_message, linked)
                if not str(args.get("content", "")).strip() and "use_result_from" not in step:
                    for j in range(i - 1, -1, -1):
                        if linked[j].get("tool") in ("compose", "web_search"):
                            step["use_result_from"] = j
                            break
            if tool == "email":
                if not str(args.get("subject", "")).strip():
                    args["subject"] = self._subject_from_message(user_message)
                if not str(args.get("body", "")).strip():
                    if "use_file_from_step" not in step and "use_result_from" not in step:
                        for j in range(i - 1, -1, -1):
                            prev_tool = linked[j].get("tool")
                            prev_action = linked[j].get("args", {}).get("action")
                            if prev_tool == "filesystem" and prev_action == "write":
                                step["use_file_from_step"] = j
                                break
                        else:
                            for j in range(i - 1, -1, -1):
                                if linked[j].get("tool") in ("compose", "web_search"):
                                    step["use_result_from"] = j
                                    break
                if not args.get("sender_name") and self._extract_regards(user_message):
                    args["sender_name"] = self._extract_regards(user_message)
            step["args"] = args
            step["tool"] = tool
            linked.append(step)
        return linked

    def _resolve_step_args(
        self,
        step: dict[str, Any],
        completed: list[dict[str, Any]],
        user_message: str = "",
    ) -> dict[str, Any]:
        tool, args = self._normalize_tool_name(
            str(step.get("tool", "")), dict(step.get("args") or {})
        )

        if "use_result_from" in step:
            idx = int(step["use_result_from"])
            if idx < 0 or idx >= len(completed):
                raise IndexError(f"use_result_from={idx} but only {len(completed)} steps completed")
            prior_output = str(completed[idx]["output"])
            if tool == "filesystem" and args.get("action") == "write":
                args["content"] = prior_output
            elif tool == "email":
                args["body"] = prior_output

        if "use_file_from_step" in step and tool == "email":
            idx = int(step["use_file_from_step"])
            if idx < 0 or idx >= len(completed):
                raise IndexError(
                    f"use_file_from_step={idx} but only {len(completed)} steps completed"
                )
            path = str(completed[idx].get("args", {}).get("path", ""))
            if not path:
                raise ValueError(f"Step {idx} has no file path to read for email body")
            args["body"] = self.filesystem.read(path)

        # Fallbacks when the planner omits linking fields
        if tool == "filesystem" and args.get("action") == "write":
            path = str(args.get("path", "")).strip()
            if not path or path == ".":
                args["path"] = self._default_write_path(user_message, completed)
            if not str(args.get("content", "")).strip() and completed:
                args["content"] = str(completed[-1]["output"])

        if tool == "email" and not str(args.get("body", "")).strip():
            for prev in reversed(completed):
                if prev.get("tool") == "filesystem" and prev.get("args", {}).get("action") == "write":
                    path = str(prev.get("args", {}).get("path", ""))
                    if path:
                        args["body"] = self.filesystem.read(path)
                        break
            if not str(args.get("body", "")).strip() and completed:
                args["body"] = str(completed[-1]["output"])

        return args

    def execute_tool(self, tool: str, args: dict[str, Any]) -> str:
        if tool == "calculator":
            return calculate(str(args.get("expression", "")))
        if tool == "compose":
            return self.compose_content(
                str(args.get("task", "")),
                str(args.get("regards", "")),
            )
        if tool == "web_search":
            results = web_search(
                str(args.get("query", "")),
                int(args.get("max_results", 5)),
            )
            return format_results(results)
        if tool == "email":
            to = str(args.get("to", "")).strip()
            if "@" not in to:
                raise ValueError(
                    f"Invalid recipient {to!r}. Use an email address (e.g. name@example.com), "
                    "not a display name alone."
                )
            body = str(args.get("body", ""))
            if not body.strip():
                raise ValueError("Email body is empty — prior step may have failed")
            subject = str(args.get("subject", "")).strip() or "Latest News Update"
            return send_email(
                to,
                subject,
                body,
                html_body=str(args["html_body"]) if args.get("html_body") else None,
                sender_name=str(args["sender_name"]) if args.get("sender_name") else None,
                always_html=bool(args.get("always_html", True)),
            )
        if tool == "filesystem":
            action = str(args.get("action", "list"))
            path = str(args.get("path", "."))
            content = str(args.get("content", ""))
            if action == "write" and not content.strip():
                raise ValueError(f"Cannot write empty content to {path}")
            return self.filesystem.run(action, path, content)
        raise ValueError(f"Unknown tool: {tool}")

    def execute_plan(
        self, steps: list[dict[str, Any]], user_message: str = ""
    ) -> list[dict[str, Any]]:
        completed: list[dict[str, Any]] = []
        for i, step in enumerate(steps):
            raw_tool = str(step.get("tool", "")).strip()
            if not raw_tool:
                raise ValueError(f"Step {i + 1} has no tool name")
            try:
                args = self._resolve_step_args(step, completed, user_message)
                tool, _ = self._normalize_tool_name(raw_tool, args)
                label = f"{tool}" + (
                    f" ({args.get('action')})" if tool == "filesystem" and args.get("action") else ""
                )
                print(f"  Step {i + 1}/{len(steps)}: {label}...", flush=True)
                output = self.execute_tool(tool, args)
            except Exception as exc:
                raise RuntimeError(
                    f"Step {i + 1} ({tool}) failed: {exc}"
                ) from exc
            completed.append(
                {
                    "step": i + 1,
                    "tool": tool,
                    "args": {k: v for k, v in args.items() if k != "content"},
                    "output": output,
                }
            )
            if tool == "filesystem" and args.get("action") == "write":
                completed[-1]["args"]["path"] = args.get("path")
                completed[-1]["args"]["bytes"] = len(str(args.get("content", "")))
        return completed

    def _format_direct_reply(
        self, user_message: str, completed: list[dict[str, Any]]
    ) -> str | None:
        if len(completed) != 1:
            return None
        item = completed[0]
        tool = item["tool"]
        output = str(item["output"])
        args = item.get("args") or {}

        if tool == "calculator":
            expr = str(args.get("expression", "")).strip()
            if expr:
                return f"The answer is {output}. ({expr})"
            return f"The answer is {output}."

        if tool == "filesystem" and args.get("action") == "read":
            path = args.get("path", "file")
            return f"Contents of {path}:\n\n{output}"

        return None

    def synthesize(
        self, user_message: str, completed: list[dict[str, Any]] | None
    ) -> str:
        if not completed:
            context = "No tools were executed."
        else:
            lines = []
            for item in completed:
                lines.append(
                    f"Step {item['step']} — {item['tool']}:\n"
                    f"Args: {json.dumps(item['args'], ensure_ascii=False)[:500]}\n"
                    f"Result: {item['output']}"
                )
            context = "Executed tool steps:\n\n" + "\n\n".join(lines)

        tools_run = {item["tool"] for item in (completed or [])}
        if tools_run == {"web_search"}:
            system = (
                "Answer the user's question using the web search results below. "
                "Be direct and informative. Do not mention email or files unless they were used."
            )
        elif tools_run <= {"filesystem"} and any(
            item.get("args", {}).get("action") == "write" for item in (completed or [])
        ):
            system = (
                "Summarize what was done. Mention files written with paths. "
                "Only mention emails if an email was actually sent."
            )
        elif "email" in tools_run:
            system = (
                "Summarize what was done: files written and emails sent (recipients, subjects). "
                "Only describe actions present in the results."
            )
        else:
            system = (
                "Answer the user based on the tool results below. Be concise and helpful. "
                "Do not invent files or emails that were not in the results."
            )

        messages = [
            {"role": "system", "content": system},
            *self.memory.to_openai_format(),
            {
                "role": "user",
                "content": f"User request: {user_message}\n\n{context}",
            },
        ]
        return self._chat(messages, temperature=0.3)

    def handle(self, user_message: str) -> str:
        user_message = user_message.strip()
        if not user_message:
            return "Please enter a message."

        self.memory.add_user(user_message)

        try:
            plan = self._plan_override(user_message) or self.plan(user_message)
        except Exception as exc:
            reply = f"I had trouble planning your request: {exc}"
            self.memory.add_assistant(reply)
            return reply

        if not plan.get("use_tools"):
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful multitask assistant. Answer clearly. "
                        "Do not ask for confirmation. Execute tasks when requested."
                    ),
                },
                *self.memory.to_openai_format(),
                {"role": "user", "content": user_message},
            ]
            reply = self._chat(messages, temperature=0.4)
            self.memory.add_assistant(reply)
            return reply

        steps = self._sanitize_plan(
            user_message,
            self._fix_plan(
                user_message,
                self._auto_link_steps(plan.get("steps") or [], user_message),
            ),
        )
        if not steps:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful multitask assistant. Answer clearly and concisely.",
                },
                *self.memory.to_openai_format(),
                {"role": "user", "content": user_message},
            ]
            reply = self._chat(messages, temperature=0.4)
            self.memory.add_assistant(reply)
            return reply

        print(f"\n[Running {len(steps)} step(s)...]")
        try:
            completed = self.execute_plan(steps, user_message)
        except Exception as exc:
            reply = f"Tool execution failed: {exc}"
            self.memory.add_assistant(reply)
            return reply

        reply = self._format_direct_reply(user_message, completed) or self.synthesize(
            user_message, completed
        )
        self.memory.add_assistant(reply)
        return reply
