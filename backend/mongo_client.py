from pymongo import MongoClient as MongoClient_
import os
from datetime import datetime

class MongoClient:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017")
        self.client = MongoClient_(mongodb_uri)
        self.db = self.client.arabic_rag
        self.chunks_collection = self.db.chunks
        self.config_collection = self.db.system_config
    
    def init_databases(self):
        if "chunks" not in self.db.list_collection_names():
            self.db.create_collection("chunks")
        
        if "system_config" not in self.db.list_collection_names():
            self.db.create_collection("system_config")
        
        default_config = {
            "chunk_size": int(os.getenv("CHUNK_SIZE", "500")),
            "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "50")),
            "top_k": int(os.getenv("TOP_K", "3")),
            "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "llm_model": os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        }
        
        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": default_config},
            upsert=True
        )
    
    def get_config(self):
        config = self.config_collection.find_one({"_id": "default"})
        return config
    
    def update_config(self, config_dict):
        config_dict['_id'] = 'default'
        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": config_dict},
            upsert=True
        )
    
    def store_chunks(self, chunks):
        chunk_ids = []
        
        for chunk in chunks:
            chunk_doc = {
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "chunk_index": chunk["chunk_index"],
                "document_id": chunk["document_id"],
                "created_at": datetime.utcnow()
            }
            
            result = self.chunks_collection.insert_one(chunk_doc)
            chunk_ids.append(str(result.inserted_id))
        
        return chunk_ids
    
    def get_chunks_by_vector_ids(self, vector_ids):
        chunks = []
        
        for vector_id in vector_ids:
            chunk = self.chunks_collection.find_one({"vector_id": vector_id})
            if chunk:
                chunks.append({
                    "content": chunk["content"],
                    "metadata": chunk["metadata"]
                })
        
        return chunks