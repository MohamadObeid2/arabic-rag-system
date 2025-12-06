from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import shutil
import tempfile

from .config import Config
from .insertion_service import InsertionService
from .retrieval_service import RetrievalService
from .models import ChatRequest, ConfigModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()
insertion_service = InsertionService(config)
retrieval_service = RetrievalService(config)

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
def chat(request: ChatRequest):
    result = retrieval_service.chat(request.question)
    return result

@app.get("/api/search")
def search(query: str):
    query_embedding = retrieval_service.embed_text(query)
    results = retrieval_service.search(query_embedding, config.top_k)
    
    return {
        "success": True,
        "query": query,
        "sources": results
    }

@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    
    uploaded_files = []
    for file in files:
        if file.filename.endswith('.txt'):
            file_path = os.path.join(temp_dir, file.filename)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content)
            })
    
    chunks = insertion_service.load_and_split_documents(temp_dir)
    insertion_service.store(chunks)
    
    shutil.rmtree(temp_dir)
    
    return {
        "success": True,
        "message": f"تم معالجة {len(uploaded_files)} وثيقة و {len(chunks)} جزء",
        "files": uploaded_files
    }

@app.get("/api/system")
def get_system():
    config_data = config.get_config()
    config_data.pop('_id', None)
    return config_data

@app.post("/api/system")
def update_system(new_config: ConfigModel):
    config.update_config(new_config)
    return {"success": True, "message": "Configuration updated"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}