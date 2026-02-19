"""System Prompt assembler — 6 components in fixed order."""

from pathlib import Path

MAX_COMPONENT_CHARS = 20000


class PromptBuilder:
    def __init__(self, base_dir: str | Path):
        self.base = Path(base_dir)

    def build(self, rag_mode: bool = False) -> str:
        components = [
            ("Skills Snapshot", self.base / "SKILLS_SNAPSHOT.md"),
            ("Soul", self.base / "workspace" / "SOUL.md"),
            ("Identity", self.base / "workspace" / "IDENTITY.md"),
            ("User Profile", self.base / "workspace" / "USER.md"),
            ("Agents Guide", self.base / "workspace" / "AGENTS.md"),
        ]

        if rag_mode:
            components.append(("RAG Mode", None))  # Placeholder text
        else:
            components.append(("Long-term Memory", self.base / "memory" / "MEMORY.md"))

        sections = []
        for label, path in components:
            if path is None:
                content = (
                    "你的长期记忆将通过 RAG 检索动态注入，无需在此加载完整记忆文件。"
                    "当你需要回忆过去的信息时，系统会自动检索相关记忆片段。"
                )
            elif path.is_file():
                content = path.read_text(encoding="utf-8")
                if len(content) > MAX_COMPONENT_CHARS:
                    content = content[:MAX_COMPONENT_CHARS] + "\n...[truncated]"
            else:
                content = f"(File not found: {path.name})"

            sections.append(f"<!-- {label} -->\n{content}")

        return "\n\n".join(sections)
