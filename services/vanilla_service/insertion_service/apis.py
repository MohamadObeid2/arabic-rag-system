from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
import shutil
import tempfile

app = FastAPI()

from .insertion_service import InsertionService
from ..shared_services.mongo_client import MongoClient

insertion_service = None
mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient()
        mongo_client.init_databases()
    return mongo_client

def get_insertion_service():
    global insertion_service
    if insertion_service is None:
        mongo = get_mongo_client()
        config_data = mongo.get_config()
        insertion_service = InsertionService(config_data)
        insertion_service.set_mongo_client(mongo)
    return insertion_service

@app.on_event("startup")
async def startup_event():
    get_insertion_service()

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="لم يتم رفع أي ملفات")
    
    temp_dir = tempfile.mkdtemp()
    
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
    
    insertion_service = get_insertion_service()
    result = insertion_service.insert(temp_dir)
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return {
        "success": True,
        "message": f"تم معالجة {result['documents']} وثيقة و {result['chunks']} جزء",
        "files": uploaded_files
    }