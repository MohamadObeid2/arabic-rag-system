from fastapi import FastAPI, HTTPException
from ..models import ChatRequest, ConfigModel

app = FastAPI()

from .retrieval_service import RetrievalService
from ..shared_services.mongo_client import MongoClient

retrieval_service = None
mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient()
        mongo_client.init_databases()
    return mongo_client

def get_retrieval_service():
    global retrieval_service
    if retrieval_service is None:
        mongo = get_mongo_client()
        config_data = mongo.get_config()
        retrieval_service = RetrievalService(config_data)
        retrieval_service.set_mongo_client(mongo)
    return retrieval_service

@app.on_event("startup")
async def startup_event():
    get_retrieval_service()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    retrieval_service = get_retrieval_service()
    result = retrieval_service.chat(request.question)
    return result

@app.get("/api/search")
async def search_documents(query: str):
    retrieval_service = get_retrieval_service()
    
    results = retrieval_service.search(query)
    return results

@app.get("/api/system")
async def get_system_config():
    mongo = get_mongo_client()
    config = mongo.get_config()
    return config

@app.post("/api/system")
async def update_system_config(config: ConfigModel):
    mongo = get_mongo_client()

    updated_config = mongo.update_config(config.dict())

    global retrieval_service
    retrieval_service = None
    get_retrieval_service()
    
    if updated_config["embedding_model_changed"]:
        retrieval_service.vector_store.delete_all_vectors()
        mongo.delete_all_chunks()
        retrieval_service.vector_store.reset_collection()
    
    return {"success": True, "message": "تم حفظ الإعدادات بنجاح"}

@app.get("/api/chunks")
async def getAllChunks(): 
    mongo = get_mongo_client()
    all_chunks = mongo.get_all_chunks()
    return {"success": True, "chunks": all_chunks}

@app.get("/api/vectors")
async def getAllVectors(): 
    retrieval_service = get_retrieval_service()
    vectors = retrieval_service.vector_store.get_all_vectors()
    return {"success": True, "vectors": vectors}

@app.get("/api/clean")
async def clear_all_data():
    retrieval_service = get_retrieval_service()
    mongo = get_mongo_client()
    
    retrieval_service.vector_store.delete_all_vectors()
    mongo.delete_all_chunks()
    
    return {"success": True, "message": "تم حذف جميع المتجهات والأجزاء بنجاح"}
    
@app.get("/api/health")
async def health_check():
    return {"status": "يعمل", "service": "Arabic Rag System"}