"""Base data connector interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator
from datetime import datetime, timedelta


class BaseDataConnector(ABC):
  """Base class for all data connectors."""
  
  def __init__(self, config: Dict[str, Any]):
    """Initialize connector with configuration."""
    self.config = config
    self.validate_config()
  
  @abstractmethod
  def validate_config(self) -> None:
    """Validate connector configuration."""
    pass
  
  @abstractmethod
  def connect(self) -> bool:
    """Establish connection to data source."""
    pass
  
  @abstractmethod
  def fetch_data(self, start_time: datetime, end_time: datetime) -> Iterator[Dict[str, Any]]:
    """Fetch data from the source within time range."""
    pass
  
  @abstractmethod
  def test_connection(self) -> bool:
    """Test if connection is working."""
    pass
  
  def get_metadata(self) -> Dict[str, Any]:
    """Get connector metadata."""
    return {
      "type": self.__class__.__name__,
      "config": self.config,
      "connected": self.test_connection()
    }
