"""Memory flush -- distill Daily Logs into MEMORY.md via LLM."""

from memory.native.daily_log import DailyLog
from memory.native.knowledge import KnowledgeStore

FLUSH_PROMPT = """You are a memory curator. Given the following daily log entries, extract the most important information that should be remembered long-term.

Current MEMORY.md contents:
{existing_memory}

Recent Daily Logs:
{daily_logs}

Rules:
1. Only keep truly important facts (user preferences, project decisions, learned skills)
2. Remove duplicates with existing MEMORY.md
3. Output the COMPLETE updated MEMORY.md content in markdown format
4. Keep the section structure: User Preferences, Project Facts, Learned Skills
5. Be concise -- each item should be one line

Output the full updated MEMORY.md content:"""


async def flush_memories(
    llm, daily_log: DailyLog, knowledge: KnowledgeStore, days: int = 7
) -> str:
    """Use LLM to distill recent daily logs into MEMORY.md."""
    recent = daily_log.read_recent(days=days)
    if not recent.strip():
        return "No recent logs to flush."

    existing = knowledge.read()
    prompt = FLUSH_PROMPT.format(existing_memory=existing, daily_logs=recent)

    response = await llm.ainvoke(prompt)
    new_content = response.content if hasattr(response, "content") else str(response)

    knowledge.write(new_content)
    return new_content
