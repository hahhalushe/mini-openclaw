"""Provider base types."""

from dataclasses import dataclass, field


@dataclass
class ProviderSpec:
    name: str
    llm_class: str
    env_key: str | None
    display_name: str
    default_model: str
    supports_embedding: bool = False
    embedding_class: str | None = None
    api_base_default: str = ""
    extra_init_kwargs: dict = field(default_factory=dict)
