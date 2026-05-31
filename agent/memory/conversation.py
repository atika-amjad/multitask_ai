from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Role = Literal["user", "assistant", "system"]


@dataclass
class Message:
    role: Role
    content: str


@dataclass
class ConversationMemory:
    max_messages: int = 40
    messages: list[Message] = field(default_factory=list)

    def add(self, role: Role, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def add_system(self, content: str) -> None:
        self.add("system", content)

    def clear(self) -> None:
        self.messages.clear()

    def to_openai_format(self) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def recent_context(self, limit: int = 10) -> str:
        recent = self.messages[-limit:]
        if not recent:
            return "(no prior messages)"
        lines = [f"{m.role}: {m.content}" for m in recent]
        return "\n".join(lines)
