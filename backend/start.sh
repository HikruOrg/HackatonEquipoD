#!/bin/bash

# Azure Image Categorizer API Startup Script

echo "🚀 Starting Azure Image Categorizer API..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create outputs directory if it doesn't exist
mkdir -p outputs

# Create mock_data directory for local testing if it doesn't exist
mkdir -p mock_data

# Check if .env file exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Azure Storage connection string"
fi

# Start the API server
echo "🌐 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload