# backend/tests/test_scaffold.py
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def test_directory_structure():
    dirs = [
        "api", "graph", "graph/engines", "graph/nodes",
        "memory", "memory/native", "memory/logs",
        "tools", "providers", "workspace", "skills",
        "sessions", "sessions/archive", "knowledge", "storage",
    ]
    for d in dirs:
        assert (BASE / d).is_dir(), f"Missing directory: {d}"


def test_workspace_files_exist():
    files = ["SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md"]
    for f in files:
        assert (BASE / "workspace" / f).is_file(), f"Missing: workspace/{f}"


def test_memory_file_exists():
    assert (BASE / "memory" / "MEMORY.md").is_file()


def test_skill_exists():
    assert (BASE / "skills" / "get_weather" / "SKILL.md").is_file()
