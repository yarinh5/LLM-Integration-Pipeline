@echo off
echo 🚀 LLM Integration Pipeline - Quick Start
echo ================================================

REM Check if we're in the right directory
if not exist "app" (
    echo ❌ Please run this script from the project root directory
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️ .env file not found. Creating from template...
    if exist "env.example" (
        copy env.example .env
        echo ✅ Created .env file
        echo 📝 Please edit .env file with your API keys before continuing
    ) else (
        echo ❌ env.example file not found
        exit /b 1
    )
)

REM Check if Docker is running
echo 🔄 Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    exit /b 1
)
echo ✅ Docker is available

REM Start the application
echo.
echo 🚀 Starting LLM Integration Pipeline...
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo 🎉 LLM Integration Pipeline is starting up!
    echo.
    echo 📊 Access points:
    echo    • Web Dashboard: http://localhost:8000
    echo    • API Documentation: http://localhost:8000/docs
    echo    • Health Check: http://localhost:8000/health
    echo.
    echo 📋 Next steps:
    echo 1. Wait for services to start (about 30 seconds)
    echo 2. Open http://localhost:8000 in your browser
    echo 3. Create a data source using the dashboard
    echo 4. Run an analysis job to test the pipeline
    echo.
    echo 🛠️ Management commands:
    echo    • View logs: docker-compose logs -f
    echo    • Stop services: docker-compose down
    echo    • Restart: docker-compose restart
) else (
    echo ❌ Failed to start services
    exit /b 1
)

pause
