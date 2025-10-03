"""Base agent interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class Anomaly(BaseModel):
  """Anomaly detection result."""
  severity: str  # low, medium, high, critical
  category: str
  description: str
  confidence: float  # 0.0 to 1.0
  data: Dict[str, Any]
  detected_at: datetime


class AnalysisResult(BaseModel):
  """Analysis result."""
  anomalies: List[Anomaly]
  summary: str
  recommendations: List[str]
  metrics: Dict[str, Any]


class BaseAgent(ABC):
  """Base class for AI agents."""
  
  def __init__(self, config: Dict[str, Any]):
    """Initialize agent with configuration."""
    self.config = config
    self.validate_config()
  
  @abstractmethod
  def validate_config(self) -> None:
    """Validate agent configuration."""
    pass
  
  @abstractmethod
  async def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
    """Analyze data and return results."""
    pass
  
  def get_agent_name(self) -> str:
    """Get agent name."""
    return self.__class__.__name__
  
  def get_agent_info(self) -> Dict[str, Any]:
    """Get agent information."""
    return {
      "name": self.get_agent_name(),
      "config": self.config,
      "capabilities": self.get_capabilities()
    }
  
  def get_capabilities(self) -> List[str]:
    """Get agent capabilities."""
    return []
