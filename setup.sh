#!/bin/bash

echo "Arabic RAG System - Setup Script"
echo "================================="

echo "1. Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing Python 3.11..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python@3.11
    else
        echo "Please install Python 3.11 manually from python.org"
        exit 1
    fi
fi

echo "2. Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please install Docker Desktop from docker.com"
        exit 1
    else
        echo "Please install Docker from docker.com"
        exit 1
    fi
fi

echo "3. Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Docker Compose included with Docker Desktop"
    fi
fi

echo "4. Creating virtual environment..."
python3 -m venv .venv

echo "5. Activating virtual environment..."
source .venv/bin/activate

echo "6. Upgrading pip..."
pip install --upgrade pip

echo "7. Installing Python requirements..."
pip install -r requirements.txt

echo "8. Downloading small models..."
if [ -f "scripts/download_small_models.py" ]; then
    python3 scripts/download_small_models.py
else
    echo "Models script not found. Creating minimal models directory..."
    mkdir -p models/embedding models/llm
    echo "Note: Models will download on first use"
fi

chmod +x run.sh
./run.sh

echo "================================="
echo "Setup completed successfully!"