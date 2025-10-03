#!/usr/bin/env python3
"""Test script for the LLM Integration Pipeline."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.data_connectors.factory import DataConnectorFactory
from app.llm.factory import LLMProviderFactory
from app.agents.anomaly_detector import AnomalyDetectorAgent
from app.reports.factory import ReportGeneratorFactory
from app.reports.base import ReportData


async def test_data_connectors():
  """Test data connectors."""
  print("🔌 Testing Data Connectors...")
  
  # Test log connector
  try:
    log_config = {
      "file_path": "data/example_logs.json",
      "log_format": "json"
    }
    
    log_connector = DataConnectorFactory.create_connector("log", log_config)
    
    if log_connector.test_connection():
      print("✅ Log connector: Connection successful")
      
      # Test data fetching
      end_time = datetime.now()
      start_time = end_time - timedelta(hours=24)
      
      data = list(log_connector.fetch_data(start_time, end_time))
      print(f"✅ Log connector: Fetched {len(data)} entries")
    else:
      print("❌ Log connector: Connection failed")
  
  except Exception as e:
    print(f"❌ Log connector test failed: {e}")
  
  # Test database connector (if database is available)
  try:
    db_config = {
      "connection_string": "postgresql://postgres:password@localhost:5432/llm_pipeline",
      "query": "SELECT 1 as test_column"
    }
    
    db_connector = DataConnectorFactory.create_connector("database", db_config)
    
    if db_connector.test_connection():
      print("✅ Database connector: Connection successful")
    else:
      print("⚠️ Database connector: Connection failed (database may not be running)")
  
  except Exception as e:
    print(f"⚠️ Database connector test failed: {e}")


async def test_llm_providers():
  """Test LLM providers."""
  print("\n🤖 Testing LLM Providers...")
  
  # Test OpenAI provider (if API key is available)
  try:
    openai_config = {
      "default_model": "gpt-3.5-turbo",
      "embedding_model": "text-embedding-ada-002"
    }
    
    openai_provider = LLMProviderFactory.create_provider("openai", openai_config)
    print("✅ OpenAI provider: Initialized successfully")
    
    # Test a simple request
    from app.llm.base import LLMMessage
    
    messages = [
      LLMMessage(role="user", content="Hello, this is a test message.")
    ]
    
    try:
      response = await openai_provider.generate_response(messages)
      print(f"✅ OpenAI provider: Response received: {response.content[:50]}...")
    except Exception as e:
      print(f"⚠️ OpenAI provider: API call failed (check API key): {e}")
  
  except Exception as e:
    print(f"⚠️ OpenAI provider test failed: {e}")
  
  # Test Anthropic provider (if API key is available)
  try:
    anthropic_config = {
      "default_model": "claude-3-sonnet-20240229"
    }
    
    anthropic_provider = LLMProviderFactory.create_provider("anthropic", anthropic_config)
    print("✅ Anthropic provider: Initialized successfully")
  
  except Exception as e:
    print(f"⚠️ Anthropic provider test failed: {e}")


async def test_anomaly_detector():
  """Test anomaly detection agent."""
  print("\n🔍 Testing Anomaly Detection Agent...")
  
  try:
    # Create sample data
    sample_data = [
      {
        "timestamp": "2024-01-01T10:00:00Z",
        "level": "INFO",
        "message": "User login successful",
        "status": 200,
        "response_time": 0.5
      },
      {
        "timestamp": "2024-01-01T10:01:00Z",
        "level": "ERROR",
        "message": "Database connection failed",
        "status": 500,
        "response_time": 5.0
      },
      {
        "timestamp": "2024-01-01T10:02:00Z",
        "level": "WARN",
        "message": "High memory usage detected",
        "status": 200,
        "response_time": 1.2
      }
    ]
    
    # Create anomaly detector
    detector_config = {
      "llm_provider": "openai",
      "sensitivity": "medium"
    }
    
    detector = AnomalyDetectorAgent(detector_config)
    print("✅ Anomaly detector: Initialized successfully")
    
    # Test analysis (this might fail if LLM API is not available)
    try:
      result = await detector.analyze(sample_data)
      print(f"✅ Anomaly detector: Analysis completed")
      print(f"   - Anomalies detected: {len(result.anomalies)}")
      print(f"   - Summary: {result.summary[:100]}...")
    except Exception as e:
      print(f"⚠️ Anomaly detector: Analysis failed (LLM API may not be available): {e}")
  
  except Exception as e:
    print(f"❌ Anomaly detector test failed: {e}")


def test_report_generators():
  """Test report generators."""
  print("\n📊 Testing Report Generators...")
  
  # Create sample report data
  report_data = ReportData(
    title="Test Analysis Report",
    summary="This is a test report generated by the pipeline.",
    anomalies=[
      {
        "severity": "high",
        "category": "error_detection",
        "description": "Multiple database connection failures detected",
        "confidence": 0.85
      },
      {
        "severity": "medium",
        "category": "performance",
        "description": "High response time detected",
        "confidence": 0.72
      }
    ],
    metrics={
      "total_entries_analyzed": 1000,
      "total_anomalies_detected": 2,
      "anomaly_rate": 0.002
    },
    recommendations=[
      "Check database connection pool configuration",
      "Monitor response times more closely"
    ],
    generated_at=datetime.utcnow(),
    data_source="Test Data Source",
    analysis_period={"start": "2024-01-01", "end": "2024-01-02"}
  )
  
  # Test HTML generator
  try:
    html_generator = ReportGeneratorFactory.create_generator("html", {})
    html_content = asyncio.run(html_generator.generate_report(report_data))
    
    if html_content and len(html_content) > 100:
      print("✅ HTML generator: Report generated successfully")
      
      # Save test report
      with open("test_report.html", "w") as f:
        f.write(html_content)
      print("✅ HTML generator: Test report saved as test_report.html")
    else:
      print("❌ HTML generator: Generated content is too short")
  
  except Exception as e:
    print(f"❌ HTML generator test failed: {e}")
  
  # Test JSON generator
  try:
    json_generator = ReportGeneratorFactory.create_generator("json", {})
    json_content = asyncio.run(json_generator.generate_report(report_data))
    
    if json_content:
      parsed = json.loads(json_content)
      if "metadata" in parsed and "anomalies" in parsed:
        print("✅ JSON generator: Report generated successfully")
        
        # Save test report
        with open("test_report.json", "w") as f:
          f.write(json_content)
        print("✅ JSON generator: Test report saved as test_report.json")
      else:
        print("❌ JSON generator: Generated content is invalid")
    else:
      print("❌ JSON generator: No content generated")
  
  except Exception as e:
    print(f"❌ JSON generator test failed: {e}")


async def main():
  """Main test function."""
  print("🧪 LLM Integration Pipeline - Test Suite")
  print("=" * 50)
  
  # Check if example data exists
  if not Path("data/example_logs.json").exists():
    print("⚠️ Example data not found. Run scripts/example_data.py first.")
    return
  
  # Run tests
  await test_data_connectors()
  await test_llm_providers()
  await test_anomaly_detector()
  test_report_generators()
  
  print("\n🎉 Test suite completed!")
  print("\nGenerated test files:")
  print("📄 test_report.html - HTML test report")
  print("📄 test_report.json - JSON test report")
  
  print("\nNext steps:")
  print("1. Check the generated test reports")
  print("2. Start the full application: docker-compose up -d")
  print("3. Access the dashboard: http://localhost:8000")


if __name__ == "__main__":
  asyncio.run(main())
