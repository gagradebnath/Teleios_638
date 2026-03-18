"""
adapters/__init__.py — ModelAdapter factory.

Usage:
    from adapters import get_adapter
    adapter = get_adapter(model_cfg)   # model_cfg = parsed config/models.json
"""
from adapters.model_adapter import ModelAdapter
from adapters.ollama_adapter import OllamaAdapter
from adapters.openai_adapter import OpenAIAdapter
# from adapters.anthropic_adapter import AnthropicAdapter
from adapters.vllm_adapter import VLLMAdapter

_REGISTRY = {
    "ollama":    OllamaAdapter,
    "openai":    OpenAIAdapter,
    # "anthropic": AnthropicAdapter,
    "vllm":      VLLMAdapter,
}


def get_adapter(model_cfg: dict) -> ModelAdapter:
    """
    Build and return the correct ModelAdapter from config/models.json.

    To switch provider, change "active_provider" in config/models.json.
    Default: ollama (uses your locally installed Ollama).
    """
    provider     = model_cfg.get("active_provider", "ollama")
    providers    = model_cfg.get("providers", {})
    provider_cfg = providers.get(provider, {})

    cls = _REGISTRY.get(provider)
    if cls is None:
        raise ValueError(
            f"Unknown model provider: '{provider}'. "
            f"Valid options: {list(_REGISTRY.keys())}"
        )
    return cls(provider_cfg)


__all__ = [
    "ModelAdapter",
    "OllamaAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "VLLMAdapter",
    "get_adapter",
]