"""Python REPL tool."""

import io
import contextlib

from langchain_core.tools import tool as lc_tool, BaseTool

MAX_OUTPUT = 5000


def create_python_repl_tool() -> BaseTool:

    @lc_tool
    def python_repl(code: str) -> str:
        """Execute Python code and return the output. Use for calculations and data processing."""
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, {"__builtins__": __builtins__})
            output = stdout.getvalue().strip()
            if len(output) > MAX_OUTPUT:
                output = output[:MAX_OUTPUT] + "\n...[truncated]"
            return output or "(no output)"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    return python_repl
