"""Native dual-layer memory backend."""

from pathlib import Path

from memory.base import MemoryBackend, MemoryItem
from memory.native.daily_log import DailyLog
from memory.native.knowledge import KnowledgeStore
from memory.native.flush import flush_memories


class NativeMemoryBackend(MemoryBackend):
    def __init__(self, memory_dir: str | Path, llm=None):
        self.memory_dir = Path(memory_dir)
        self.daily_log = DailyLog(self.memory_dir / "logs")
        self.knowledge = KnowledgeStore(self.memory_dir / "MEMORY.md")
        self.llm = llm

    async def add_memory(self, content: str, metadata: dict | None = None) -> None:
        self.daily_log.append(content)

    async def search_memory(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        # Simple text search -- proper vector search added in Task 13
        all_text = self.knowledge.read()
        lines = [
            l.strip("- ").strip()
            for l in all_text.splitlines()
            if l.strip().startswith("- ")
        ]
        query_lower = query.lower()
        scored = [
            (line, sum(1 for w in query_lower.split() if w in line.lower()))
            for line in lines
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            MemoryItem(content=line, score=score, source="MEMORY.md")
            for line, score in scored[:top_k]
            if score > 0
        ]

    async def get_all(self) -> str:
        return self.knowledge.read()

    async def flush(self) -> None:
        if self.llm:
            await flush_memories(self.llm, self.daily_log, self.knowledge)
