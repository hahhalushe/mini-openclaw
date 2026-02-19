"""Layer 2: MEMORY.md -- curated long-term knowledge base."""

from pathlib import Path


class KnowledgeStore:
    def __init__(self, memory_file: str | Path):
        self.path = Path(memory_file)

    def read(self) -> str:
        """Read the full MEMORY.md content."""
        if self.path.is_file():
            return self.path.read_text(encoding="utf-8")
        return ""

    def write(self, content: str) -> None:
        """Overwrite MEMORY.md with new content."""
        self.path.write_text(content, encoding="utf-8")

    def append_section(self, section: str, content: str) -> None:
        """Append content under a specific section heading."""
        current = self.read()
        marker = f"## {section}"
        if marker in current:
            # Insert before the next section or at end
            parts = current.split(marker, 1)
            after = parts[1] if len(parts) > 1 else ""
            # Find next ## heading
            next_section = after.find("\n## ")
            if next_section != -1:
                insert_point = next_section
                updated = (
                    parts[0]
                    + marker
                    + after[:insert_point].rstrip()
                    + f"\n- {content}\n"
                    + after[insert_point:]
                )
            else:
                updated = parts[0] + marker + after.rstrip() + f"\n- {content}\n"
        else:
            updated = current.rstrip() + f"\n\n## {section}\n\n- {content}\n"
        self.write(updated)
