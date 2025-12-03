Arabic RAG System - Offline

A simple Arabic Retrieval-Augmented Generation system that runs completely offline.

Features:
- Process Arabic text documents (.txt files)
- Local embedding model (all-MiniLM-L6-v2)
- Local LLM (TinyLlama-1.1B-Chat)
- MongoDB for document storage
- Milvus for vector search
- Modern Arabic interface
- Bulk document upload
- Configurable parameters
- Search functionality

Requirements:
- Docker and Docker Compose
- Python 3.8+
- 4GB+ RAM
- Internet connection for first model download

Setup:
1. Run: chmod +x run.sh
2. Run: ./run.sh

The script will:
- Start MongoDB and Milvus containers
- Install Python dependencies
- Start the web server

Open: http://localhost:8000

Folder Structure:
- backend/: FastAPI server
- frontend/: HTML/CSS/JS interface
- models/: Local model files (downloaded automatically)
- dataset/: Your Arabic text files
- scripts/: Utility scripts

API Endpoints:
- GET /: Frontend interface
- POST /api/chat: Chat with documents
- POST /api/upload: Upload text files
- GET/POST /api/system: System configuration
- GET /api/search: Search vectors
- GET /health: Health check

Configuration:
Edit .env file for database settings
Models can be changed from web interface

Default Models:
- Embedding: all-MiniLM-L6-v2
- LLM: TinyLlama/TinyLlama-1.1B-Chat-v1.0

Troubleshooting:
- Check Docker is running
- Check ports 27017 and 19530 are free
- Run download scripts if models fail
- Check console for errors

Note: First run downloads models (3-5GB). Ensure stable internet.