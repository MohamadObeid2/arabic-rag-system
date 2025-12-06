from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import shutil
import tempfile
import uuid
from datetime import datetime

from .config import Config
from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .llm_service import LLMService
from .rag_service import RAGService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()
embedding_service = EmbeddingService(config)
vector_store = VectorStore(config, embedding_service)
llm_service = LLMService(config)
rag_service = RAGService(config, vector_store, llm_service)
chunking_service = ChunkingService(config)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def get_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>نظام RAG العربي يعمل</h1>")

@app.post("/api/chat")
def chat(question: str):
    result = rag_service.chat(question)
    return result

@app.get("/api/search")
def search(query: str):
    result = rag_service.search_documents(query)
    return result

@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    
    uploaded_files = []
    for file in files:
        if not file.filename.endswith('.txt'):
            continue
        
        file_path = os.path.join(temp_dir, file.filename)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        uploaded_files.append(file.filename)
    
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No text files found")
    
    documents = chunking_service.load_and_split_documents(temp_dir)
    
    embeddings = embedding_service.embed_documents(documents)
    
    chunk_ids = []
    for doc in documents:
        chunk_id = str(uuid.uuid4())
        chunk_ids.append(chunk_id)
        
        config.chunks_collection.insert_one({
            "chunk_id": chunk_id,
            "content": doc["content"],
            "metadata": doc["metadata"],
            "created_at": datetime.utcnow()
        })
    
    vector_store.add_documents(documents, embeddings, chunk_ids)
    
    shutil.rmtree(temp_dir)
    
    return {
        "success": True,
        "documents": len(documents),
        "files": uploaded_files
    }

@app.get("/api/system")
def get_system():
    config_data = config.get_config()
    config_data.pop('_id', None)
    return config_data

@app.post("/api/system")
def update_system(new_config: dict):
    config.update_config(new_config)
    return {"success": True, "message": "Configuration updated"}

@app.get("/api/chunks")
def get_chunks():
    chunks = list(config.chunks_collection.find({}, {"_id": 0}))
    return {"chunks": chunks}

@app.get("/api/clean")
def clean_all():
    vector_store.delete_all()
    config.chunks_collection.delete_many({})
    return {"success": True, "message": "All data cleared"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}