"""Tool registration factory."""

from pathlib import Path

from langchain_core.tools import BaseTool

from tools.terminal_tool import create_terminal_tool
from tools.python_repl_tool import create_python_repl_tool
from tools.read_file_tool import create_read_file_tool
from tools.fetch_url_tool import create_fetch_url_tool
from tools.search_knowledge_tool import create_search_knowledge_tool


def get_all_tools(base_dir: str | Path, retriever=None) -> list[BaseTool]:
    base_dir = str(Path(base_dir).resolve())
    return [
        create_terminal_tool(root_dir=base_dir),
        create_python_repl_tool(),
        create_read_file_tool(root_dir=base_dir),
        create_fetch_url_tool(),
        create_search_knowledge_tool(retriever=retriever),
    ]
