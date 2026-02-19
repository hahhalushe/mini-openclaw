# backend/tests/test_tools_advanced.py
from tools.skills_scanner import scan_skills, generate_snapshot, write_snapshot
from pathlib import Path
import tempfile


def test_skills_scanner():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill_dir = base / "skills" / "test_skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test\ndescription: a test skill\n---\n\nHello"
        )
        skills = scan_skills(base / "skills")
        assert len(skills) == 1
        assert skills[0]["name"] == "test"


def test_generate_snapshot():
    skills = [{"name": "weather", "description": "Get weather", "location": "./skills/weather/SKILL.md"}]
    snap = generate_snapshot(skills)
    assert "<name>weather</name>" in snap
    assert "<available_skills>" in snap


def test_write_snapshot():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "skills" / "demo").mkdir(parents=True)
        (base / "skills" / "demo" / "SKILL.md").write_text(
            "---\nname: demo\ndescription: demo skill\n---\n"
        )
        content = write_snapshot(base)
        assert "<name>demo</name>" in content
        assert (base / "SKILLS_SNAPSHOT.md").exists()


def test_fetch_url_tool_exists():
    from tools.fetch_url_tool import create_fetch_url_tool
    tool = create_fetch_url_tool()
    assert tool.name == "fetch_url"


def test_search_knowledge_tool_no_retriever():
    from tools.search_knowledge_tool import create_search_knowledge_tool
    tool = create_search_knowledge_tool(retriever=None)
    result = tool.invoke({"query": "test"})
    assert "not yet initialized" in result.lower()
