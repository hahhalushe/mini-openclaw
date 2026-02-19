"""Tests for CreateAgentEngine initialization and structure."""


def test_create_agent_engine_init():
    """Verify CreateAgentEngine stores llm and tools on construction."""
    from graph.engines.create_agent_engine import CreateAgentEngine

    class MockLLM:
        pass

    engine = CreateAgentEngine(llm=MockLLM(), tools=[])
    assert engine.llm is not None
    assert engine.tools == []


def test_create_agent_engine_is_base_engine():
    """Verify CreateAgentEngine is a subclass of BaseEngine."""
    from graph.engines.base import BaseEngine
    from graph.engines.create_agent_engine import CreateAgentEngine

    assert issubclass(CreateAgentEngine, BaseEngine)
