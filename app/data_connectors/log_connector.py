"""Log file data connector."""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, Iterator, List
from app.data_connectors.base import BaseDataConnector


class LogConnector(BaseDataConnector):
  """Connector for log files."""
  
  def validate_config(self) -> None:
    """Validate log connector configuration."""
    required_fields = ["file_path", "log_format"]
    for field in required_fields:
      if field not in self.config:
        raise ValueError(f"Missing required field: {field}")
    
    if not os.path.exists(self.config["file_path"]):
      raise FileNotFoundError(f"Log file not found: {self.config['file_path']}")
  
  def connect(self) -> bool:
    """Test file accessibility."""
    return os.access(self.config["file_path"], os.R_OK)
  
  def test_connection(self) -> bool:
    """Test if log file is accessible."""
    return self.connect()
  
  def fetch_data(self, start_time: datetime, end_time: datetime) -> Iterator[Dict[str, Any]]:
    """Fetch log entries within time range."""
    log_format = self.config["log_format"]
    
    with open(self.config["file_path"], "r", encoding="utf-8") as file:
      for line_num, line in enumerate(file, 1):
        try:
          parsed_entry = self._parse_log_line(line, log_format)
          if parsed_entry and self._is_in_time_range(parsed_entry, start_time, end_time):
            parsed_entry["line_number"] = line_num
            parsed_entry["raw_line"] = line.strip()
            yield parsed_entry
        except Exception as e:
          # Log parsing error but continue
          continue
  
  def _parse_log_line(self, line: str, log_format: str) -> Dict[str, Any]:
    """Parse log line based on format."""
    if log_format == "json":
      return json.loads(line.strip())
    
    elif log_format == "apache_common":
      return self._parse_apache_common(line)
    
    elif log_format == "nginx":
      return self._parse_nginx(line)
    
    elif log_format == "custom":
      return self._parse_custom(line)
    
    else:
      raise ValueError(f"Unsupported log format: {log_format}")
  
  def _parse_apache_common(self, line: str) -> Dict[str, Any]:
    """Parse Apache Common Log Format."""
    pattern = r'(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]*)" (\d+) (\S+)'
    match = re.match(pattern, line)
    
    if not match:
      return None
    
    return {
      "ip": match.group(1),
      "identity": match.group(2),
      "user": match.group(3),
      "timestamp": match.group(4),
      "request": match.group(5),
      "status": int(match.group(6)),
      "size": match.group(7)
    }
  
  def _parse_nginx(self, line: str) -> Dict[str, Any]:
    """Parse Nginx log format."""
    # Basic nginx format parsing
    parts = line.split()
    if len(parts) < 7:
      return None
    
    return {
      "ip": parts[0],
      "timestamp": parts[3] + " " + parts[4],
      "method": parts[5].strip('"'),
      "url": parts[6],
      "status": int(parts[8]) if len(parts) > 8 else None,
      "response_time": parts[9] if len(parts) > 9 else None
    }
  
  def _parse_custom(self, line: str) -> Dict[str, Any]:
    """Parse custom log format using regex."""
    if "regex_pattern" not in self.config:
      raise ValueError("Custom format requires regex_pattern in config")
    
    pattern = self.config["regex_pattern"]
    match = re.match(pattern, line)
    
    if not match:
      return None
    
    # Extract named groups
    return match.groupdict()
  
  def _is_in_time_range(self, entry: Dict[str, Any], start_time: datetime, end_time: datetime) -> bool:
    """Check if log entry is within time range."""
    timestamp_str = entry.get("timestamp")
    if not timestamp_str:
      return True  # Include entries without timestamp
    
    try:
      # Try different timestamp formats
      for fmt in ["%d/%b/%Y:%H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
        try:
          entry_time = datetime.strptime(timestamp_str, fmt)
          return start_time <= entry_time <= end_time
        except ValueError:
          continue
      
      return True  # Include if can't parse timestamp
    except Exception:
      return True
