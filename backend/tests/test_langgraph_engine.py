"""Tests for LangGraph engine and routing logic."""

from unittest.mock import Mock


def test_langgraph_engine_builds_graph():
    """Verify the StateGraph compiles without errors."""
    from graph.engines.langgraph_engine import LangGraphEngine

    class MockLLM:
        pass

    engine = LangGraphEngine(llm=MockLLM(), tools=[], memory_dir="")
    assert engine.graph is not None


def test_should_continue_no_tool_calls():
    """When last_response is None, route to 'reflect'."""
    from graph.engines.langgraph_engine import should_continue

    state = {"last_response": None, "iteration": 0}
    assert should_continue(state) == "reflect"


def test_should_continue_with_tool_calls():
    """When last_response has tool_calls, route to 'act'."""
    from graph.engines.langgraph_engine import should_continue

    mock_response = Mock()
    mock_response.tool_calls = [{"name": "test", "args": {}}]
    state = {"last_response": mock_response, "iteration": 0}
    assert should_continue(state) == "act"


def test_should_continue_max_iterations():
    """When iteration >= MAX_ITERATIONS, route to 'reflect' even with tool_calls."""
    from graph.engines.langgraph_engine import should_continue, MAX_ITERATIONS

    mock_response = Mock()
    mock_response.tool_calls = [{"name": "test", "args": {}}]
    state = {"last_response": mock_response, "iteration": MAX_ITERATIONS}
    assert should_continue(state) == "reflect"


def test_should_continue_empty_tool_calls():
    """When last_response has empty tool_calls list, route to 'reflect'."""
    from graph.engines.langgraph_engine import should_continue

    mock_response = Mock()
    mock_response.tool_calls = []
    state = {"last_response": mock_response, "iteration": 0}
    assert should_continue(state) == "reflect"
