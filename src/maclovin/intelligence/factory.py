"""Factory for creating LLM Provider instances based on configuration."""

from typing import Optional
from maclovin.models import AIConfig
from maclovin.intelligence.base import BaseLLMProvider
from maclovin.intelligence.gemini_provider import GeminiProvider
from maclovin.intelligence.openai_provider import OpenAIProvider


def create_llm_provider(config: AIConfig) -> Optional[BaseLLMProvider]:
    """Cria e retorna a instância do provedor de IA conforme configurado."""
    provider_type = config.provider.lower().strip()

    if provider_type == "gemini":
        return GeminiProvider(config)
    elif provider_type in ("openai", "nvidia", "glm", "ollama", "anthropic", "groq", "deepseek", "openrouter"):
        return OpenAIProvider(config)
    else:
        print(f"[WARN] Provedor de IA desconhecido '{provider_type}'. Usando adaptador OpenAI/compatíveis.")
        return OpenAIProvider(config)
