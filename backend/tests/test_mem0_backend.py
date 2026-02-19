# backend/tests/test_mem0_backend.py
"""Tests for Mem0 backend — graceful handling when mem0 is not configured."""
import asyncio


def test_mem0_backend_init():
    from memory.mem0_backend import Mem0MemoryBackend

    # Should not crash even if mem0 isn't configured
    backend = Mem0MemoryBackend(user_id="test_user")
    assert backend.user_id == "test_user"


def test_mem0_backend_interface():
    from memory.mem0_backend import Mem0MemoryBackend
    from memory.base import MemoryBackend

    assert issubclass(Mem0MemoryBackend, MemoryBackend)


def test_mem0_backend_graceful_no_config():
    from memory.mem0_backend import Mem0MemoryBackend

    backend = Mem0MemoryBackend(user_id="test_user")
    # Should not crash, just return empty/placeholder results
    results = asyncio.run(backend.search_memory("test"))
    assert isinstance(results, list)

    all_mem = asyncio.run(backend.get_all())
    assert isinstance(all_mem, str)

    # add_memory should not crash
    asyncio.run(backend.add_memory("test content"))

    # flush should not crash
    asyncio.run(backend.flush())
