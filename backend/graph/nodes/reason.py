"""LLM reasoning node -- calls the model and returns response."""

from langchain_core.messages import AIMessage


async def reason_node(state: dict) -> dict:
    """Call LLM with current messages. Returns updated state with AI response."""
    llm = state["llm"]
    messages = state["messages"]
    tools = state.get("tools", [])

    if tools:
        llm_with_tools = llm.bind_tools(tools)
        response: AIMessage = await llm_with_tools.ainvoke(messages)
    else:
        response = await llm.ainvoke(messages)

    return {"messages": messages + [response], "last_response": response}
