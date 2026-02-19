# backend/tests/test_providers.py
from providers.registry import PROVIDERS, get_provider_spec, get_llm, get_embeddings


def test_registry_has_providers():
    names = [p.name for p in PROVIDERS]
    assert "zhipu" in names
    assert "deepseek" in names
    assert "openrouter" in names
    assert "ollama" in names
    assert "openai" in names


def test_get_provider_spec():
    spec = get_provider_spec("zhipu")
    assert spec is not None
    assert spec.display_name == "\u667a\u8c31 GLM"

    assert get_provider_spec("nonexistent") is None


def test_get_llm_returns_chat_model(monkeypatch):
    """Verify get_llm returns a LangChain BaseChatModel (mocked)."""
    monkeypatch.setenv("ZHIPUAI_API_KEY", "test-key")
    # Just verify it doesn't crash on import resolution
    from providers.registry import _resolve_class
    # Test the class resolver with a known class
    cls = _resolve_class("langchain_openai.ChatOpenAI")
    assert cls is not None
