@echo off
REM Azure Image Categorizer API Startup Script for Windows

echo 🚀 Starting Azure Image Categorizer API...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create outputs directory if it doesn't exist
if not exist "outputs" mkdir outputs

REM Create mock_data directory for local testing if it doesn't exist  
if not exist "mock_data" mkdir mock_data

REM Check if .env file exists, if not copy from example
if not exist ".env" (
    echo 📝 Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your Azure Storage connection string
)

REM Start the API server
echo 🌐 Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

uvicorn app:app --host 0.0.0.0 --port 8000 --reload