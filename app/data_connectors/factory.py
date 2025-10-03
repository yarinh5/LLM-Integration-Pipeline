"""Data connector factory."""

from typing import Dict, Any, Type
from app.data_connectors.base import BaseDataConnector
from app.data_connectors.log_connector import LogConnector
from app.data_connectors.database_connector import DatabaseConnector
from app.data_connectors.api_connector import APIConnector


class DataConnectorFactory:
  """Factory for creating data connectors."""
  
  _connectors: Dict[str, Type[BaseDataConnector]] = {
    "log": LogConnector,
    "database": DatabaseConnector,
    "api": APIConnector
  }
  
  @classmethod
  def create_connector(cls, connector_type: str, config: Dict[str, Any]) -> BaseDataConnector:
    """Create a data connector instance."""
    if connector_type not in cls._connectors:
      raise ValueError(f"Unknown connector type: {connector_type}")
    
    connector_class = cls._connectors[connector_type]
    return connector_class(config)
  
  @classmethod
  def get_available_connectors(cls) -> list[str]:
    """Get list of available connector types."""
    return list(cls._connectors.keys())
  
  @classmethod
  def register_connector(cls, connector_type: str, connector_class: Type[BaseDataConnector]) -> None:
    """Register a new connector type."""
    cls._connectors[connector_type] = connector_class
