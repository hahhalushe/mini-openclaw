# backend/tests/test_memory_native.py
import tempfile
from pathlib import Path

import pytest


def test_daily_log_append_and_read():
    from memory.native.daily_log import DailyLog

    with tempfile.TemporaryDirectory() as td:
        dl = DailyLog(td)
        dl.append("User likes Python")
        dl.append("Project uses FastAPI")
        content = dl.read_recent(days=1)
        assert "User likes Python" in content
        assert "Project uses FastAPI" in content


def test_daily_log_list():
    from memory.native.daily_log import DailyLog

    with tempfile.TemporaryDirectory() as td:
        dl = DailyLog(td)
        dl.append("test entry")
        logs = dl.list_logs()
        assert len(logs) == 1


def test_knowledge_store_read_write():
    from memory.native.knowledge import KnowledgeStore

    with tempfile.TemporaryDirectory() as td:
        ks = KnowledgeStore(Path(td) / "MEMORY.md")
        ks.write("# Memory\n\n## Facts\n- Fact 1")
        content = ks.read()
        assert "Fact 1" in content


def test_knowledge_store_append_section():
    from memory.native.knowledge import KnowledgeStore

    with tempfile.TemporaryDirectory() as td:
        ks = KnowledgeStore(Path(td) / "MEMORY.md")
        ks.write("# Memory\n\n## User Preferences\n\n(empty)\n\n## Project Facts\n\n(empty)")
        ks.append_section("User Preferences", "Likes dark mode")
        content = ks.read()
        assert "Likes dark mode" in content


def test_native_backend_add_and_search():
    from memory.native import NativeMemoryBackend

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "MEMORY.md").write_text(
            "# Memory\n\n## Facts\n\n- Python is great\n- FastAPI for backend\n"
        )
        (base / "logs").mkdir()
        backend = NativeMemoryBackend(memory_dir=td)
        import asyncio

        asyncio.run(backend.add_memory("New fact"))
        results = asyncio.run(backend.search_memory("Python"))
        assert len(results) > 0
        assert "Python" in results[0].content


def test_memory_backend_interface():
    from memory.base import MemoryBackend, MemoryItem

    # Verify abstract interface
    assert hasattr(MemoryBackend, "add_memory")
    assert hasattr(MemoryBackend, "search_memory")
    assert hasattr(MemoryBackend, "get_all")
    assert hasattr(MemoryBackend, "flush")
    # Verify MemoryItem
    item = MemoryItem(content="test", score=0.5, source="test.md")
    assert item.content == "test"
