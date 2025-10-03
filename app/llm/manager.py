"""LLM manager for handling multiple providers."""

from typing import Dict, Any, List, Optional
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.llm.factory import LLMProviderFactory


class LLMManager:
  """Manager for LLM providers."""
  
  def __init__(self):
    """Initialize LLM manager."""
    self.providers: Dict[str, BaseLLMProvider] = {}
    self.default_provider: Optional[str] = None
  
  def add_provider(self, name: str, provider_type: str, config: Dict[str, Any]) -> None:
    """Add a new LLM provider."""
    provider = LLMProviderFactory.create_provider(provider_type, config)
    self.providers[name] = provider
    
    if self.default_provider is None:
      self.default_provider = name
  
  def set_default_provider(self, name: str) -> None:
    """Set default provider."""
    if name not in self.providers:
      raise ValueError(f"Provider '{name}' not found")
    self.default_provider = name
  
  def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
    """Get LLM provider by name or default."""
    provider_name = name or self.default_provider
    if not provider_name or provider_name not in self.providers:
      raise ValueError(f"Provider '{provider_name}' not found")
    return self.providers[provider_name]
  
  async def generate_response(
    self,
    messages: List[LLMMessage],
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
  ) -> LLMResponse:
    """Generate response using specified or default provider."""
    provider = self.get_provider(provider_name)
    return await provider.generate_response(
      messages=messages,
      model=model,
      temperature=temperature,
      max_tokens=max_tokens
    )
  
  async def generate_embeddings(
    self,
    texts: List[str],
    provider_name: Optional[str] = None,
    model: Optional[str] = None
  ) -> List[List[float]]:
    """Generate embeddings using specified or default provider."""
    provider = self.get_provider(provider_name)
    return await provider.generate_embeddings(texts=texts, model=model)
  
  def get_available_providers(self) -> List[str]:
    """Get list of available provider names."""
    return list(self.providers.keys())
  
  def get_provider_info(self, name: str) -> Dict[str, Any]:
    """Get provider information."""
    if name not in self.providers:
      raise ValueError(f"Provider '{name}' not found")
    
    provider = self.providers[name]
    return {
      "name": name,
      "type": provider.get_provider_name(),
      "available_models": provider.get_available_models(),
      "metadata": provider.get_metadata() if hasattr(provider, 'get_metadata') else {}
    }
