"""Database data connector."""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from typing import Dict, Any, Iterator, List
from app.data_connectors.base import BaseDataConnector


class DatabaseConnector(BaseDataConnector):
  """Connector for database queries."""
  
  def validate_config(self) -> None:
    """Validate database connector configuration."""
    required_fields = ["connection_string", "query"]
    for field in required_fields:
      if field not in self.config:
        raise ValueError(f"Missing required field: {field}")
  
  def connect(self) -> bool:
    """Establish database connection."""
    try:
      self.engine = create_engine(self.config["connection_string"])
      # Test connection
      with self.engine.connect() as conn:
        conn.execute(text("SELECT 1"))
      return True
    except Exception:
      return False
  
  def test_connection(self) -> bool:
    """Test database connection."""
    return self.connect()
  
  def fetch_data(self, start_time: datetime, end_time: datetime) -> Iterator[Dict[str, Any]]:
    """Fetch data using configured query."""
    query = self.config["query"]
    
    # Replace time placeholders if they exist
    if "{start_time}" in query:
      query = query.replace("{start_time}", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    if "{end_time}" in query:
      query = query.replace("{end_time}", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
      with self.engine.connect() as conn:
        result = conn.execute(text(query))
        
        for row in result:
          # Convert row to dictionary
          row_dict = dict(row._mapping)
          yield row_dict
    
    except Exception as e:
      raise Exception(f"Database query failed: {str(e)}")
  
  def fetch_dataframe(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
    """Fetch data as pandas DataFrame."""
    query = self.config["query"]
    
    # Replace time placeholders
    if "{start_time}" in query:
      query = query.replace("{start_time}", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    if "{end_time}" in query:
      query = query.replace("{end_time}", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
      return pd.read_sql(query, self.engine)
    except Exception as e:
      raise Exception(f"Database query failed: {str(e)}")
  
  def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
    """Get table schema information."""
    query = f"""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """
    
    try:
      with self.engine.connect() as conn:
        result = conn.execute(text(query))
        return [dict(row._mapping) for row in result]
    except Exception as e:
      raise Exception(f"Failed to get table schema: {str(e)}")
