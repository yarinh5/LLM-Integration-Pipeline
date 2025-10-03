#!/usr/bin/env python3
"""Setup script for LLM Integration Pipeline."""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
  """Run a command and handle errors."""
  print(f"🔄 {description}...")
  try:
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    print(f"✅ {description} completed successfully")
    return True
  except subprocess.CalledProcessError as e:
    print(f"❌ {description} failed: {e.stderr}")
    return False


def check_requirements():
  """Check if required tools are installed."""
  print("🔍 Checking requirements...")
  
  requirements = {
    "python": "python --version",
    "pip": "pip --version",
    "docker": "docker --version",
    "docker-compose": "docker-compose --version"
  }
  
  missing = []
  for tool, command in requirements.items():
    if not run_command(command, f"Checking {tool}"):
      missing.append(tool)
  
  if missing:
    print(f"❌ Missing required tools: {', '.join(missing)}")
    print("Please install the missing tools and run this script again.")
    return False
  
  print("✅ All requirements satisfied")
  return True


def setup_environment():
  """Set up environment files."""
  print("🔧 Setting up environment...")
  
  env_file = Path(".env")
  env_example = Path("env.example")
  
  if not env_file.exists() and env_example.exists():
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your API keys and configuration")
  elif env_file.exists():
    print("✅ .env file already exists")
  else:
    print("❌ env.example file not found")
    return False
  
  return True


def install_dependencies():
  """Install Python dependencies."""
  print("📦 Installing Python dependencies...")
  
  if not run_command("pip install -r requirements.txt", "Installing dependencies"):
    return False
  
  return True


def setup_database():
  """Set up database using Docker."""
  print("🗄️ Setting up database...")
  
  if not run_command("docker-compose up -d db redis", "Starting database and Redis"):
    return False
  
  print("⏳ Waiting for database to be ready...")
  import time
  time.sleep(10)
  
  return True


def run_migrations():
  """Run database migrations."""
  print("🔄 Running database migrations...")
  
  # The database tables are created automatically when the app starts
  # This is handled in app/database.py
  print("✅ Database migrations completed")
  return True


def create_directories():
  """Create necessary directories."""
  print("📁 Creating directories...")
  
  directories = ["logs", "data", "static", "reports"]
  
  for directory in directories:
    Path(directory).mkdir(exist_ok=True)
    print(f"✅ Created directory: {directory}")
  
  return True


def main():
  """Main setup function."""
  print("🚀 LLM Integration Pipeline Setup")
  print("=" * 40)
  
  # Check if we're in the right directory
  if not Path("app").exists() or not Path("requirements.txt").exists():
    print("❌ Please run this script from the project root directory")
    sys.exit(1)
  
  steps = [
    ("Checking requirements", check_requirements),
    ("Setting up environment", setup_environment),
    ("Installing dependencies", install_dependencies),
    ("Creating directories", create_directories),
    ("Setting up database", setup_database),
    ("Running migrations", run_migrations)
  ]
  
  for step_name, step_func in steps:
    print(f"\n📋 {step_name}")
    if not step_func():
      print(f"❌ Setup failed at: {step_name}")
      sys.exit(1)
  
  print("\n🎉 Setup completed successfully!")
  print("\nNext steps:")
  print("1. Edit .env file with your API keys")
  print("2. Start the application: docker-compose up -d")
  print("3. Access the dashboard: http://localhost:8000")
  print("4. Check API documentation: http://localhost:8000/docs")


if __name__ == "__main__":
  main()
