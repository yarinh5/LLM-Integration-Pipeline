"""API data connector."""

import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, Iterator, List, Optional
from app.data_connectors.base import BaseDataConnector


class APIConnector(BaseDataConnector):
  """Connector for REST APIs."""
  
  def validate_config(self) -> None:
    """Validate API connector configuration."""
    required_fields = ["base_url", "endpoint"]
    for field in required_fields:
      if field not in self.config:
        raise ValueError(f"Missing required field: {field}")
  
  def connect(self) -> bool:
    """Test API connectivity."""
    return self.test_connection()
  
  def test_connection(self) -> bool:
    """Test API connection."""
    try:
      response = httpx.get(
        f"{self.config['base_url']}{self.config['endpoint']}",
        headers=self.config.get("headers", {}),
        timeout=10
      )
      return response.status_code < 400
    except Exception:
      return False
  
  def fetch_data(self, start_time: datetime, end_time: datetime) -> Iterator[Dict[str, Any]]:
    """Fetch data from API."""
    # For synchronous iteration, we'll collect all data first
    all_data = self._fetch_all_data(start_time, end_time)
    for item in all_data:
      yield item
  
  def _fetch_all_data(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Fetch all data from API."""
    base_url = self.config["base_url"]
    endpoint = self.config["endpoint"]
    headers = self.config.get("headers", {})
    params = self.config.get("params", {})
    
    # Add time parameters if supported
    if self.config.get("supports_time_filter", False):
      params.update({
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
      })
    
    all_data = []
    page = 1
    
    while True:
      # Add pagination if supported
      if self.config.get("supports_pagination", False):
        params["page"] = page
        params["per_page"] = self.config.get("page_size", 100)
      
      try:
        response = httpx.get(
          f"{base_url}{endpoint}",
          headers=headers,
          params=params,
          timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
          items = data
        elif isinstance(data, dict):
          items = data.get("data", data.get("results", [data]))
        else:
          items = [data]
        
        if not items:
          break
        
        all_data.extend(items)
        
        # Check if there are more pages
        if not self.config.get("supports_pagination", False):
          break
        
        # Check for pagination indicators
        if isinstance(data, dict):
          if "next" not in data or not data["next"]:
            break
          if "has_next" in data and not data["has_next"]:
            break
        
        page += 1
        
        # Safety limit
        if page > 1000:
          break
      
      except Exception as e:
        print(f"API request failed: {e}")
        break
    
    return all_data
  
  async def fetch_data_async(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Async version of data fetching."""
    async with httpx.AsyncClient() as client:
      base_url = self.config["base_url"]
      endpoint = self.config["endpoint"]
      headers = self.config.get("headers", {})
      params = self.config.get("params", {})
      
      if self.config.get("supports_time_filter", False):
        params.update({
          "start_time": start_time.isoformat(),
          "end_time": end_time.isoformat()
        })
      
      all_data = []
      page = 1
      
      while True:
        if self.config.get("supports_pagination", False):
          params["page"] = page
          params["per_page"] = self.config.get("page_size", 100)
        
        try:
          response = await client.get(
            f"{base_url}{endpoint}",
            headers=headers,
            params=params,
            timeout=30
          )
          response.raise_for_status()
          
          data = response.json()
          
          if isinstance(data, list):
            items = data
          elif isinstance(data, dict):
            items = data.get("data", data.get("results", [data]))
          else:
            items = [data]
          
          if not items:
            break
          
          all_data.extend(items)
          
          if not self.config.get("supports_pagination", False):
            break
          
          if isinstance(data, dict):
            if "next" not in data or not data["next"]:
              break
            if "has_next" in data and not data["has_next"]:
              break
          
          page += 1
          
          if page > 1000:
            break
        
        except Exception as e:
          print(f"Async API request failed: {e}")
          break
      
      return all_data
