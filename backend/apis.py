from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from typing import List
import os
import shutil
import tempfile

app = FastAPI()

from .models import ChatRequest, SystemConfig
from .rag_service import RAGService
from .mongo_client import MongoClient

rag_service = None
mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient()
        mongo_client.init_databases()
    return mongo_client

def get_rag_service():
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
        rag_service.set_mongo_client(get_mongo_client())
    return rag_service

@app.get("/")
async def get_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>نظام RAG العربي يعمل</h1>")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    mongo = get_mongo_client()
    config_data = mongo.get_config()
    rag = get_rag_service()
    
    try:
        result = rag.search(request.question, config_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="لم يتم رفع أي ملفات")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        uploaded_files = []
        
        for file in files:
            if not file.filename.lower().endswith('.txt'):
                continue
                
            file_path = os.path.join(temp_dir, file.filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content)
            })
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="لم يتم العثور على ملفات نصية")
        
        mongo = get_mongo_client()
        config_data = mongo.get_config()
        rag = get_rag_service()
        
        result = rag.insert(temp_dir, config_data)
        
        return {
            "success": True,
            "message": f"تم معالجة {result['documents']} وثيقة و {result['chunks']} جزء",
            "files": uploaded_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في المعالجة: {str(e)}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.get("/api/system")
async def get_system_config():
    mongo = get_mongo_client()
    config = mongo.get_config()
    if config:
        config.pop('_id', None)
        return config
    return SystemConfig().dict()

@app.post("/api/system")
async def update_system_config(config: SystemConfig):
    try:
        mongo = get_mongo_client()
        config_dict = config.dict()
        mongo.update_config(config_dict)
        
        global rag_service
        rag_service = None
        
        return {"success": True, "message": "تم حفظ الإعدادات بنجاح"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الحفظ: {str(e)}")

@app.get("/api/search")
async def search_documents(query: str, top_k: int = 5):
    mongo = get_mongo_client()
    config_data = mongo.get_config()
    rag = get_rag_service()
    
    question_embedding = rag.embedding_service.embed_text(query, config_data.get("embedding_model", "all-MiniLM-L6-v2"))
    
    if question_embedding:
        results = rag.vector_store.search(question_embedding, top_k, config_data.get("similarity_threshold", 0.3))
        return {"success": True, "results": results}
    
    return {"success": False, "results": []}

@app.get("/health")
async def health_check():
    return {"status": "يعمل", "service": "arabic_rag"}