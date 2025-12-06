from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from typing import List
import os
import shutil
import tempfile

app = FastAPI()

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
        mongo = get_mongo_client()
        config_data = mongo.get_config()
        rag_service = RAGService(config_data)
        rag_service.set_mongo_client(mongo)
    return rag_service

@app.on_event("startup")
async def startup_event():
    get_rag_service()

@app.get("/")
async def get_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>نظام RAG العربي يعمل</h1>")

@app.post("/api/chat")
async def chat(request):
    rag_service = get_rag_service()
    
    try:
        result = rag_service.retrieve(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@app.get("/api/search")
async def search_documents(query: str):
    rag_service = get_rag_service()
    
    results = rag_service.search(query)
    return results

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
        
        rag_service = get_rag_service()
        result = rag_service.insert(temp_dir)
        
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
    return config

@app.post("/api/system")
async def update_system_config(config):
    try:
        mongo = get_mongo_client()

        updated_config = mongo.update_config(config.dict())

        # reload models
        global rag_service
        rag_service = None
        get_rag_service()
        
        # clean milvus collection and delete all data
        if updated_config["embedding_model_changed"]:
            rag_service.vector_store.delete_all_vectors()
            mongo.delete_all_chunks()
            rag_service.vector_store.reset_collection()
        
        return {"success": True, "message": "تم حفظ الإعدادات بنجاح"}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"خطأ في الحفظ: {str(e)}")

@app.get("/api/chunks")
async def getAllChunks(): 
    mongo = get_mongo_client()
    all_chunks = mongo.get_all_chunks()
    return {"success": True, "chunks": all_chunks}

@app.get("/api/vectors")
async def getAllVectors(): 
    rag_service = get_rag_service()
    vectors = rag_service.vector_store.get_all_vectors()
    return {"success": True, "vectors": vectors}

@app.get("/api/clean")
async def clear_all_data():
    rag_service = get_rag_service()
    mongo = get_mongo_client()
    
    rag_service.vector_store.delete_all_vectors()
    mongo.delete_all_chunks()
    
    return {"success": True, "message": "تم حذف جميع المتجهات والأجزاء بنجاح"}
    
@app.get("/api/health")
async def health_check():
    return {"status": "يعمل", "service": "Arabic Rag System"}