# run.ps1

param(
    [string]$service = "both"
)

Write-Host "Setting up Arabic RAG System..."
Write-Host "================================"

# 1. Check Docker
Write-Host "1. Checking Docker..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Please install Docker first."
    exit 1
}

# 2. Check Python
Write-Host "2. Checking Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Please install Python 3.8+ first."
    exit 1
}

# 3. Activate virtual environment
Write-Host "3. Setting virtual environment..."
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Please run setup.ps1 first."
    exit 1
}

# 4. Start Docker containers
Write-Host "4. Starting Docker containers..."
docker compose up -d

# 5. Wait 5 seconds
Write-Host "5. Waiting for 5 sec for containers to fully initialize..."
Start-Sleep -Seconds 5

# 6. Test MongoDB connection
Write-Host "6. Testing MongoDB connection..."
python -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://admin:password@localhost:27017')
    client.admin.command('ping')
    print('✅ MongoDB connected successfully')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"

# 7. Test Milvus connection
Write-Host "7. Testing Milvus connection..."
python -c "
from pymilvus import connections
try:
    connections.connect(host='localhost', port='19530')
    print('✅ Milvus connected successfully')
    connections.disconnect('default')
except Exception as e:
    print(f'✗ Milvus connection failed: {e}')
"

# 8. Start the application
Write-Host "8. Starting the application..."

if ($service -eq "vanilla") {
    Write-Host "Starting Vanilla application..."
    uvicorn services.vanilla_service.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir services/vanilla_service
    Write-Host "✅ Started Vanilla application: http://localhost:8000"
}

if ($service -eq "langchain") {
    Write-Host "Starting Langchain application..."
    uvicorn services.langchain_service.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir services/langchain_service
    Write-Host "✅ Started Langchain application: http://localhost:8000"
}