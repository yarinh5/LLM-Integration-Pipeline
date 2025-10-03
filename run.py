#!/usr/bin/env python3
"""Quick start script for LLM Integration Pipeline."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
  """Run a command and handle errors."""
  print(f"🔄 {description}...")
  try:
    result = subprocess.run(command, shell=True, check=True)
    print(f"✅ {description} completed")
    return True
  except subprocess.CalledProcessError as e:
    print(f"❌ {description} failed: {e}")
    return False


def main():
  """Main function."""
  print("🚀 LLM Integration Pipeline - Quick Start")
  print("=" * 50)
  
  # Check if we're in the right directory
  if not Path("app").exists():
    print("❌ Please run this script from the project root directory")
    sys.exit(1)
  
  # Check if .env exists
  if not Path(".env").exists():
    print("⚠️ .env file not found. Creating from template...")
    if Path("env.example").exists():
      run_command("cp env.example .env", "Creating .env file")
      print("📝 Please edit .env file with your API keys before continuing")
    else:
      print("❌ env.example file not found")
      sys.exit(1)
  
  # Check if Docker is running
  if not run_command("docker --version", "Checking Docker"):
    print("❌ Docker is not installed or not running")
    sys.exit(1)
  
  # Start the application
  print("\n🚀 Starting LLM Integration Pipeline...")
  
  if run_command("docker-compose up -d", "Starting services"):
    print("\n🎉 LLM Integration Pipeline is starting up!")
    print("\n📊 Access points:")
    print("   • Web Dashboard: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n📋 Next steps:")
    print("1. Wait for services to start (about 30 seconds)")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Create a data source using the dashboard")
    print("4. Run an analysis job to test the pipeline")
    
    print("\n🛠️ Management commands:")
    print("   • View logs: docker-compose logs -f")
    print("   • Stop services: docker-compose down")
    print("   • Restart: docker-compose restart")
    
  else:
    print("❌ Failed to start services")
    sys.exit(1)


if __name__ == "__main__":
  main()
