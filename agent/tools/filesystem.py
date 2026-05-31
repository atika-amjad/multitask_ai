from __future__ import annotations

from pathlib import Path
from typing import Literal


Action = Literal["read", "write", "list"]


class FilesystemTool:
    def __init__(self, workspace_root: Path | None = None):
        self.root = (workspace_root or Path.cwd()).resolve()

    def _resolve(self, path: str) -> Path:
        target = (self.root / path).resolve()
        if not str(target).startswith(str(self.root)):
            raise PermissionError(f"Path escapes workspace: {path}")
        return target

    def read(self, path: str) -> str:
        target = self._resolve(path)
        if not target.is_file():
            raise FileNotFoundError(f"Not a file: {path}")
        return target.read_text(encoding="utf-8")

    def write(self, path: str, content: str) -> str:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"

    def list_dir(self, path: str = ".") -> str:
        target = self._resolve(path)
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = []
        for entry in entries:
            prefix = "[dir] " if entry.is_dir() else "[file]"
            rel = entry.relative_to(self.root)
            lines.append(f"{prefix} {rel}")
        return "\n".join(lines) if lines else "(empty directory)"

    def run(self, action: Action, path: str = ".", content: str = "") -> str:
        if action == "read":
            return self.read(path)
        if action == "write":
            return self.write(path, content)
        if action == "list":
            return self.list_dir(path)
        raise ValueError(f"Unknown action: {action}")
