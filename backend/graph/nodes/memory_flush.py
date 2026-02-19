"""Memory flush node -- writes reflection results to Daily Log."""

import json
from datetime import date
from pathlib import Path

import json_repair


async def memory_flush_node(state: dict) -> dict:
    """Parse reflection output and append to daily log."""
    reflection = state.get("reflection", "")
    memory_dir = state.get("memory_dir")
    if not reflection or not memory_dir:
        return state

    try:
        parsed = json.loads(json_repair.repair_json(reflection))
        memories = parsed.get("memories", [])
    except Exception:
        memories = []

    if memories:
        log_path = Path(memory_dir) / "logs" / f"{date.today().isoformat()}.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"- {m}" for m in memories]
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return {**state, "flushed_memories": memories}
