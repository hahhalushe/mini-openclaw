"""Sandboxed terminal tool."""

import subprocess
from pathlib import Path

from langchain_core.tools import tool as lc_tool, BaseTool

BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", "shutdown",
    ":(){", "fork bomb", "> /dev/sda", "chmod -R 777 /",
]
MAX_OUTPUT = 5000
TIMEOUT = 30


def create_terminal_tool(root_dir: str) -> BaseTool:
    root = Path(root_dir).resolve()

    @lc_tool
    def terminal(command: str) -> str:
        """Execute a shell command in a sandboxed environment. Use for system operations."""
        cmd_lower = command.lower().strip()
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return "Blocked: dangerous command detected."
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=TIMEOUT, cwd=str(root),
            )
            output = (result.stdout + result.stderr).strip()
            if len(output) > MAX_OUTPUT:
                output = output[:MAX_OUTPUT] + "\n...[truncated]"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "Blocked: command timed out (30s limit)."
        except Exception as e:
            return f"Error: {e}"

    return terminal
