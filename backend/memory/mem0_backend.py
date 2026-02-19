# backend/memory/mem0_backend.py
"""Mem0 alternate memory backend — MaaS comparison for teaching."""

from __future__ import annotations

from memory.base import MemoryBackend, MemoryItem


class Mem0MemoryBackend(MemoryBackend):
    """Memory backend using Mem0's managed memory service.

    Teaching comparison point:
    - Native backend: transparent, file-based, git-trackable, manually editable
    - Mem0 backend: automatic structuring, entity extraction, managed service
    """

    def __init__(self, user_id: str = "default_user", api_key: str | None = None):
        self.user_id = user_id
        self._memory = None
        self._api_key = api_key
        self._init_mem0()

    def _init_mem0(self):
        """Initialize Mem0 client. Gracefully handles import failure."""
        try:
            from mem0 import Memory

            config = {}
            if self._api_key:
                config["api_key"] = self._api_key
            self._memory = Memory.from_config(config) if config else Memory()
        except ImportError:
            self._memory = None
        except Exception:
            self._memory = None

    async def add_memory(self, content: str, metadata: dict | None = None) -> None:
        if self._memory is None:
            return
        try:
            self._memory.add(content, user_id=self.user_id, metadata=metadata or {})
        except Exception:
            pass

    async def search_memory(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        if self._memory is None:
            return []
        try:
            results = self._memory.search(query, user_id=self.user_id, limit=top_k)
            items = []
            for r in results:
                if isinstance(r, dict):
                    items.append(
                        MemoryItem(
                            content=r.get("memory", r.get("text", str(r))),
                            score=r.get("score", 0.0),
                            source="mem0",
                        )
                    )
            return items
        except Exception:
            return []

    async def get_all(self) -> str:
        if self._memory is None:
            return "(Mem0 not initialized)"
        try:
            all_memories = self._memory.get_all(user_id=self.user_id)
            lines = []
            for m in all_memories:
                if isinstance(m, dict):
                    lines.append(f"- {m.get('memory', m.get('text', str(m)))}")
            return "\n".join(lines) if lines else "(No memories stored)"
        except Exception:
            return "(Error retrieving memories)"

    async def flush(self) -> None:
        # Mem0 handles memory management internally
        pass
