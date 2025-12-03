#!/bin/bash

echo "Setting up Arabic RAG System..."
echo "================================"

echo "1. Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

echo "2. Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "3. Checking virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "4. Installing requirements..."
pip install -r requirements.txt

echo "5. Starting Docker containers..."
docker-compose up -d

echo "6. Waiting for services to start..."
sleep 10

echo "7. Testing MongoDB connection..."
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://admin:password@localhost:27017')
    client.admin.command('ping')
    print('✓ MongoDB connected successfully')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"

echo "8. Starting the application..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
echo "9. Application started!"
echo "Open browser: http://localhost:8000"