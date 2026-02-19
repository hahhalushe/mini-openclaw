"""Abstract base for all agent engines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator


@dataclass
class AgentEvent:
    """Unified event emitted by all engines."""
    type: str  # "token" | "tool_start" | "tool_end" | "new_response" | "retrieval" | "done" | "error"
    data: dict[str, Any]


class BaseEngine(ABC):
    @abstractmethod
    async def astream(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
    ) -> AsyncIterator[AgentEvent]:
        """Stream agent events for a single user message."""
        ...
