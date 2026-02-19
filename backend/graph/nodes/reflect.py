"""Reflection node -- agent reviews the conversation for memorable information."""

from langchain_core.messages import HumanMessage

REFLECT_PROMPT = """Review the conversation above. Extract any information worth remembering long-term:
- User preferences or habits
- Project facts or decisions
- Successful tool usage patterns
- Key dates or names

Respond with a JSON object: {"memories": ["memory 1", "memory 2", ...]}
If nothing is worth remembering, respond with: {"memories": []}
"""


async def reflect_node(state: dict) -> dict:
    """Ask LLM to reflect on conversation and extract memories."""
    llm = state["llm"]
    messages = list(state["messages"])
    messages.append(HumanMessage(content=REFLECT_PROMPT))

    response = await llm.ainvoke(messages)
    return {**state, "reflection": response.content}
