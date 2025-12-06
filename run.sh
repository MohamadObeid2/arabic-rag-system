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

echo "5. Waiting for 10 sec for containers to fully initialize..."
sleep 10

echo "6. Testing MongoDB connection..."
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://admin:password@localhost:27017')
    client.admin.command('ping')
    print('✅ MongoDB connected successfully')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"

echo "7. Testing Milvus connection..."
python3 -c "
from pymilvus import connections
try:
    connections.connect(host='localhost', port='19530')
    print('✅ Milvus connected successfully')
    connections.disconnect('default')
except Exception as e:
    print(f'✗ Milvus connection failed: {e}')
"

echo "8. Starting the application..."
./stop.sh

echo "✅ Vanilla application started successfully: http://localhost:8000"
echo "✅ Langchain application started successfully: http://localhost:8001"

uvicorn services.vanilla_service.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir services/vanilla_service &
uvicorn services.langchain_service.main:app --host 0.0.0.0 --port 8001 --reload --reload-dir services/langchain_service &
wait