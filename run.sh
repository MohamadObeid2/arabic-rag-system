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

echo "3. Setting virtual environment..."
source .venv/bin/activate

echo "4. Starting Docker containers..."
docker compose up -d
sleep 5

echo "5. Testing MongoDB connection..."
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://admin:password@localhost:27017')
    client.admin.command('ping')
    print('✅ MongoDB connected successfully')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"

echo "6. Testing Milvus connection..."
python3 -c "
from pymilvus import connections
try:
    connections.connect(host='localhost', port='19530')
    print('✅ Milvus connected successfully')
    connections.disconnect('default')
except Exception as e:
    print(f'✗ Milvus connection failed: {e}')
"

echo "7. Starting the application..."
pid=$(lsof -ti tcp:80)
if [ -n "$pid" ]; then
    kill -9 $pid
    sleep 5
fi

echo "✅ Application started successfully: http://localhost:8000"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload