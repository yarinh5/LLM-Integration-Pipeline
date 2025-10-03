"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
  """LLM message model."""
  role: str  # system, user, assistant
  content: str


class LLMResponse(BaseModel):
  """LLM response model."""
  content: str
  usage: Optional[Dict[str, Any]] = None
  model: Optional[str] = None
  finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
  """Base class for LLM providers."""
  
  def __init__(self, config: Dict[str, Any]):
    """Initialize provider with configuration."""
    self.config = config
    self.validate_config()
  
  @abstractmethod
  def validate_config(self) -> None:
    """Validate provider configuration."""
    pass
  
  @abstractmethod
  async def generate_response(
    self,
    messages: List[LLMMessage],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
  ) -> LLMResponse:
    """Generate response from LLM."""
    pass
  
  @abstractmethod
  async def generate_embeddings(
    self,
    texts: List[str],
    model: Optional[str] = None
  ) -> List[List[float]]:
    """Generate embeddings for texts."""
    pass
  
  def get_available_models(self) -> List[str]:
    """Get list of available models."""
    return self.config.get("available_models", [])
  
  def get_provider_name(self) -> str:
    """Get provider name."""
    return self.__class__.__name__
