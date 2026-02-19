"""Sandboxed file reader tool."""

from pathlib import Path

from langchain_core.tools import tool as lc_tool, BaseTool

MAX_OUTPUT = 10000


def create_read_file_tool(root_dir: str) -> BaseTool:
    root = Path(root_dir).resolve()

    @lc_tool
    def read_file(path: str) -> str:
        """Read the contents of a file within the project directory."""
        target = (root / path).resolve()
        if not str(target).startswith(str(root)):
            return "Access denied: path traversal detected."
        if not target.is_file():
            return f"Error: file not found: {path}"
        try:
            content = target.read_text(encoding="utf-8")
            if len(content) > MAX_OUTPUT:
                content = content[:MAX_OUTPUT] + "\n...[truncated]"
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    return read_file
