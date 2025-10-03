#!/usr/bin/env python3
"""Script to create example data for testing the LLM Integration Pipeline."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_log_data(num_entries=1000):
  """Generate example log data."""
  print("📝 Generating example log data...")
  
  log_entries = []
  base_time = datetime.now() - timedelta(hours=24)
  
  # Common log patterns
  error_messages = [
    "Connection timeout to database",
    "Memory allocation failed",
    "Authentication failed for user",
    "File not found: config.json",
    "Invalid request format",
    "Rate limit exceeded",
    "Service unavailable",
    "Internal server error"
  ]
  
  warning_messages = [
    "High memory usage detected",
    "Slow query execution",
    "Deprecated API endpoint used",
    "Cache miss rate high",
    "Connection pool exhausted"
  ]
  
  info_messages = [
    "User login successful",
    "Data backup completed",
    "Scheduled task executed",
    "Configuration updated",
    "Health check passed"
  ]
  
  status_codes = [200, 201, 400, 401, 403, 404, 500, 502, 503]
  
  for i in range(num_entries):
    # Add some time variation
    timestamp = base_time + timedelta(
      minutes=random.randint(0, 1440),
      seconds=random.randint(0, 59)
    )
    
    # Determine log level and message
    rand = random.random()
    if rand < 0.05:  # 5% errors
      level = "ERROR"
      message = random.choice(error_messages)
      status = random.choice([400, 401, 403, 404, 500, 502, 503])
    elif rand < 0.15:  # 10% warnings
      level = "WARN"
      message = random.choice(warning_messages)
      status = random.choice([200, 201, 400, 401])
    else:  # 80% info
      level = "INFO"
      message = random.choice(info_messages)
      status = random.choice([200, 201])
    
    # Generate some anomalies
    if random.random() < 0.02:  # 2% chance of anomaly
      # Spike in errors
      if random.random() < 0.5:
        level = "ERROR"
        message = "CRITICAL: System overload detected"
        status = 500
      else:
        # Unusual pattern
        message = f"ANOMALY: Unusual request pattern detected - {random.randint(1000, 9999)} requests in 1 minute"
        status = 429
    
    entry = {
      "timestamp": timestamp.isoformat(),
      "level": level,
      "message": message,
      "status": status,
      "response_time": random.uniform(0.1, 2.0),
      "ip": f"192.168.1.{random.randint(1, 254)}",
      "user_id": f"user_{random.randint(1000, 9999)}",
      "endpoint": random.choice([
        "/api/users",
        "/api/orders",
        "/api/products",
        "/api/auth/login",
        "/api/health",
        "/api/metrics"
      ]),
      "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
      "user_agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
      ])
    }
    
    log_entries.append(entry)
  
  # Sort by timestamp
  log_entries.sort(key=lambda x: x["timestamp"])
  
  # Save to file
  log_file = Path("data/example_logs.json")
  log_file.parent.mkdir(exist_ok=True)
  
  with open(log_file, "w") as f:
    for entry in log_entries:
      f.write(json.dumps(entry) + "\n")
  
  print(f"✅ Generated {num_entries} log entries in {log_file}")
  return log_file


def generate_database_data():
  """Generate example database data."""
  print("🗄️ Generating example database data...")
  
  # This would typically connect to a real database
  # For now, we'll create a SQL file with sample data
  sql_file = Path("data/example_database.sql")
  sql_file.parent.mkdir(exist_ok=True)
  
  sql_content = """
-- Example database schema and data for LLM Integration Pipeline

CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB
);

-- Insert sample user activity data
INSERT INTO user_activity (user_id, action, timestamp, ip_address, user_agent, success, error_message) VALUES
(1001, 'login', NOW() - INTERVAL '1 hour', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', TRUE, NULL),
(1002, 'purchase', NOW() - INTERVAL '2 hours', '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', TRUE, NULL),
(1003, 'login', NOW() - INTERVAL '3 hours', '192.168.1.102', 'Mozilla/5.0 (X11; Linux x86_64)', FALSE, 'Invalid credentials'),
(1001, 'logout', NOW() - INTERVAL '4 hours', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', TRUE, NULL),
(1004, 'register', NOW() - INTERVAL '5 hours', '192.168.1.103', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', TRUE, NULL);

-- Insert sample system metrics
INSERT INTO system_metrics (metric_name, metric_value, timestamp, tags) VALUES
('cpu_usage', 45.2, NOW() - INTERVAL '1 hour', '{"host": "web-server-01", "environment": "production"}'),
('memory_usage', 78.5, NOW() - INTERVAL '1 hour', '{"host": "web-server-01", "environment": "production"}'),
('disk_usage', 32.1, NOW() - INTERVAL '1 hour', '{"host": "web-server-01", "environment": "production"}'),
('response_time', 150.5, NOW() - INTERVAL '1 hour', '{"host": "web-server-01", "environment": "production", "endpoint": "/api/users"}'),
('error_rate', 2.3, NOW() - INTERVAL '1 hour', '{"host": "web-server-01", "environment": "production"}');
"""
  
  with open(sql_file, "w") as f:
    f.write(sql_content)
  
  print(f"✅ Generated database schema and sample data in {sql_file}")
  return sql_file


def create_example_configs():
  """Create example configuration files."""
  print("⚙️ Creating example configurations...")
  
  configs = {
    "log_source.json": {
      "name": "Game Server Logs",
      "type": "log",
      "config": {
        "file_path": "data/example_logs.json",
        "log_format": "json"
      }
    },
    "database_source.json": {
      "name": "User Activity Database",
      "type": "database",
      "config": {
        "connection_string": "postgresql://postgres:password@localhost:5432/llm_pipeline",
        "query": "SELECT * FROM user_activity WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'"
      }
    },
    "api_source.json": {
      "name": "External API",
      "type": "api",
      "config": {
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoint": "/posts",
        "headers": {"Content-Type": "application/json"},
        "supports_pagination": True,
        "supports_time_filter": False
      }
    }
  }
  
  config_dir = Path("data/configs")
  config_dir.mkdir(exist_ok=True)
  
  for filename, config in configs.items():
    config_file = config_dir / filename
    with open(config_file, "w") as f:
      json.dump(config, f, indent=2)
    print(f"✅ Created {config_file}")
  
  return config_dir


def main():
  """Main function to generate all example data."""
  print("🎯 LLM Integration Pipeline - Example Data Generator")
  print("=" * 50)
  
  # Create data directory
  Path("data").mkdir(exist_ok=True)
  
  # Generate example data
  generate_log_data(1000)
  generate_database_data()
  create_example_configs()
  
  print("\n🎉 Example data generation completed!")
  print("\nGenerated files:")
  print("📁 data/")
  print("  ├── example_logs.json (1000 log entries)")
  print("  ├── example_database.sql (database schema and data)")
  print("  └── configs/")
  print("      ├── log_source.json")
  print("      ├── database_source.json")
  print("      └── api_source.json")
  
  print("\nNext steps:")
  print("1. Start the application: docker-compose up -d")
  print("2. Create data sources using the example configs")
  print("3. Run analysis jobs to test the pipeline")


if __name__ == "__main__":
  main()
