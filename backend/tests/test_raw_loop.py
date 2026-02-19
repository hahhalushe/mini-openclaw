import pytest
from graph.engines.base import AgentEvent


def test_agent_event_creation():
    event = AgentEvent(type="token", data={"content": "hello"})
    assert event.type == "token"
    assert event.data["content"] == "hello"


def test_raw_loop_engine_instantiation():
    from graph.engines.raw_loop_engine import RawLoopEngine
    engine = RawLoopEngine(
        api_base="http://localhost:8000/v1",
        api_key="test",
        model="test-model",
        tools=[],
        tool_executor={},
    )
    assert engine.model == "test-model"
