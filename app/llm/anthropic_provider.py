"""Anthropic LLM provider."""

from typing import List, Dict, Any, Optional
import anthropic
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.config import settings


class AnthropicProvider(BaseLLMProvider):
  """Anthropic LLM provider."""
  
  def validate_config(self) -> None:
    """Validate Anthropic configuration."""
    if not settings.anthropic_api_key:
      raise ValueError("Anthropic API key is required")
    
    self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
  
  async def generate_response(
    self,
    messages: List[LLMMessage],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
  ) -> LLMResponse:
    """Generate response using Anthropic API."""
    model = model or self.config.get("default_model", "claude-3-sonnet-20240229")
    
    # Convert messages to Anthropic format
    system_message = None
    user_messages = []
    
    for msg in messages:
      if msg.role == "system":
        system_message = msg.content
      else:
        user_messages.append({
          "role": msg.role,
          "content": msg.content
        })
    
    try:
      response = await self.client.messages.create(
        model=model,
        messages=user_messages,
        system=system_message,
        temperature=temperature,
        max_tokens=max_tokens or 1000
      )
      
      return LLMResponse(
        content=response.content[0].text,
        usage={
          "input_tokens": response.usage.input_tokens,
          "output_tokens": response.usage.output_tokens
        },
        model=response.model,
        finish_reason=response.stop_reason
      )
    
    except Exception as e:
      raise Exception(f"Anthropic API error: {str(e)}")
  
  async def generate_embeddings(
    self,
    texts: List[str],
    model: Optional[str] = None
  ) -> List[List[float]]:
    """Generate embeddings using Anthropic API."""
    # Anthropic doesn't have embeddings API, so we'll use a workaround
    # or suggest using OpenAI for embeddings
    raise NotImplementedError("Anthropic doesn't provide embeddings API. Use OpenAI for embeddings.")
  
  def get_available_models(self) -> List[str]:
    """Get available Anthropic models."""
    return [
      "claude-3-opus-20240229",
      "claude-3-sonnet-20240229",
      "claude-3-haiku-20240307"
    ]
