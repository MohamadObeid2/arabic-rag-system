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

        default_exists = self.config_collection.find_one({"_id": "default"})
        
        if not default_exists:
            default_config = {
                "chunk_size": int(os.getenv("CHUNK_SIZE", "500")),
                "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "50")),
                "top_k": int(os.getenv("TOP_K", "3")),
                "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                "llm_model": os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
                "embedding_model_changed": False,
            }
            self.config_collection.insert_one({"_id": "default", **default_config})
    
    def get_config(self):
        config = self.config_collection.find_one({"_id": "default"})
        return config
    
    def update_config(self, prev_config, new_config):

        if prev_config["embedding_model"] != new_config["embedding_model"]:
            new_config["embedding_model_changed"] = True

        new_config['_id'] = 'default'
        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": new_config},
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
    
    def get_chunks_by_vector_ids(self, vectors):
        chunks = []
        for vector in vectors:
            vector_id = vector["vector_id"]
            chunk = self.chunks_collection.find_one({"vector_id": int(vector_id)})
            if chunk:
                chunks.append({
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "score": vector["score"],
                })
                
        return chunks
    
    def get_all_chunks(self):
        chunks = []
        cursor = self.chunks_collection.find({})
        for chunk in cursor:
            chunks.append({
                "content": chunk.get("content"),
                "metadata": chunk.get("metadata"),
                "chunk_index": chunk.get("chunk_index"),
                "document_id": chunk.get("document_id"),
                "vector_id": chunk.get("vector_id"),
                "created_at": chunk.get("created_at")
            })
        return chunks