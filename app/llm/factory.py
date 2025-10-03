"""LLM provider factory."""

from typing import Dict, Any, Type
from app.llm.base import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.anthropic_provider import AnthropicProvider


class LLMProviderFactory:
  """Factory for creating LLM providers."""
  
  _providers: Dict[str, Type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider
  }
  
  @classmethod
  def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> BaseLLMProvider:
    """Create an LLM provider instance."""
    if provider_type not in cls._providers:
      raise ValueError(f"Unknown provider type: {provider_type}")
    
    provider_class = cls._providers[provider_type]
    return provider_class(config)
  
  @classmethod
  def get_available_providers(cls) -> list[str]:
    """Get list of available provider types."""
    return list(cls._providers.keys())
  
  @classmethod
  def register_provider(cls, provider_type: str, provider_class: Type[BaseLLMProvider]) -> None:
    """Register a new provider type."""
    cls._providers[provider_type] = provider_class
