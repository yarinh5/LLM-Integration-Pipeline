"""Configuration settings for the LLM Integration Pipeline."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
  """Application settings."""
  
  # Database
  database_url: str = "postgresql://postgres:password@localhost:5432/llm_pipeline"
  
  # Redis
  redis_url: str = "redis://localhost:6379/0"
  
  # LLM APIs
  openai_api_key: Optional[str] = None
  anthropic_api_key: Optional[str] = None
  
  # Application
  secret_key: str = "your-secret-key-change-in-production"
  debug: bool = False
  log_level: str = "INFO"
  
  # Monitoring
  prometheus_port: int = 9090
  
  class Config:
    env_file = ".env"
    case_sensitive = False


settings = Settings()
