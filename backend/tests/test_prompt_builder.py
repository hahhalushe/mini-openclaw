# backend/tests/test_prompt_builder.py
import tempfile
from pathlib import Path


def test_build_system_prompt():
    from graph.prompt_builder import PromptBuilder
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "workspace").mkdir()
        (base / "workspace" / "SOUL.md").write_text("# Soul\nBe kind.")
        (base / "workspace" / "IDENTITY.md").write_text("# Identity\nI am Bot.")
        (base / "workspace" / "USER.md").write_text("# User\nUnknown.")
        (base / "workspace" / "AGENTS.md").write_text("# Agents\nFollow rules.")
        (base / "memory").mkdir()
        (base / "memory" / "MEMORY.md").write_text("# Memory\nEmpty.")
        (base / "SKILLS_SNAPSHOT.md").write_text("<available_skills></available_skills>")

        pb = PromptBuilder(base_dir=td)
        prompt = pb.build()
        assert "Soul" in prompt
        assert "Identity" in prompt
        assert "Memory" in prompt
        assert "available_skills" in prompt


def test_truncation():
    from graph.prompt_builder import PromptBuilder
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "workspace").mkdir()
        # Create oversized file
        (base / "workspace" / "SOUL.md").write_text("X" * 25000)
        (base / "workspace" / "IDENTITY.md").write_text("ok")
        (base / "workspace" / "USER.md").write_text("ok")
        (base / "workspace" / "AGENTS.md").write_text("ok")
        (base / "memory").mkdir()
        (base / "memory" / "MEMORY.md").write_text("ok")
        (base / "SKILLS_SNAPSHOT.md").write_text("ok")

        pb = PromptBuilder(base_dir=td)
        prompt = pb.build()
        assert "...[truncated]" in prompt
