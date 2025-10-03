"""OpenAI LLM provider."""

from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.config import settings


class OpenAIProvider(BaseLLMProvider):
  """OpenAI LLM provider."""
  
  def validate_config(self) -> None:
    """Validate OpenAI configuration."""
    if not settings.openai_api_key:
      raise ValueError("OpenAI API key is required")
    
    self.client = AsyncOpenAI(api_key=settings.openai_api_key)
  
  async def generate_response(
    self,
    messages: List[LLMMessage],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
  ) -> LLMResponse:
    """Generate response using OpenAI API."""
    model = model or self.config.get("default_model", "gpt-3.5-turbo")
    
    # Convert messages to OpenAI format
    openai_messages = [
      {"role": msg.role, "content": msg.content}
      for msg in messages
    ]
    
    try:
      response = await self.client.chat.completions.create(
        model=model,
        messages=openai_messages,
        temperature=temperature,
        max_tokens=max_tokens
      )
      
      return LLMResponse(
        content=response.choices[0].message.content,
        usage={
          "prompt_tokens": response.usage.prompt_tokens,
          "completion_tokens": response.usage.completion_tokens,
          "total_tokens": response.usage.total_tokens
        },
        model=response.model,
        finish_reason=response.choices[0].finish_reason
      )
    
    except Exception as e:
      raise Exception(f"OpenAI API error: {str(e)}")
  
  async def generate_embeddings(
    self,
    texts: List[str],
    model: Optional[str] = None
  ) -> List[List[float]]:
    """Generate embeddings using OpenAI API."""
    model = model or self.config.get("embedding_model", "text-embedding-ada-002")
    
    try:
      response = await self.client.embeddings.create(
        model=model,
        input=texts
      )
      
      return [embedding.embedding for embedding in response.data]
    
    except Exception as e:
      raise Exception(f"OpenAI embeddings error: {str(e)}")
  
  def get_available_models(self) -> List[str]:
    """Get available OpenAI models."""
    return [
      "gpt-4",
      "gpt-4-turbo",
      "gpt-3.5-turbo",
      "gpt-3.5-turbo-16k"
    ]
