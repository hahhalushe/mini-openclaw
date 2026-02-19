# backend/memory/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MemoryItem:
    content: str
    score: float = 0.0
    source: str = ""


class MemoryBackend(ABC):
    @abstractmethod
    async def add_memory(self, content: str, metadata: dict | None = None) -> None: ...

    @abstractmethod
    async def search_memory(self, query: str, top_k: int = 5) -> list[MemoryItem]: ...

    @abstractmethod
    async def get_all(self) -> str: ...

    @abstractmethod
    async def flush(self) -> None: ...
