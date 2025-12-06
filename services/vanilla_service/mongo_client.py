from pymongo import MongoClient as MongoClient_
import os
import json
from datetime import datetime

class MongoClient:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017")
        self.client = MongoClient_(mongodb_uri)
        self.db = self.client.arabic_rag
        self.chunks_collection = self.db.chunks
        self.config_collection = self.db.system_config
        self.config = None
    
    def init_databases(self):
        if "chunks" not in self.db.list_collection_names():
            self.db.create_collection("chunks")
            
        if "system_config" not in self.db.list_collection_names():
            self.db.create_collection("system_config")
            
        self.config = self.config_collection.find_one({"_id": "default"})
        
        if not self.config:
            self.config = {
                "chunk_size": int(os.getenv("CHUNK_SIZE", "500")),
                "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "50")),
                "top_k": int(os.getenv("TOP_K", "3")),
                "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                "llm_model": os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
                "embedding_dim": os.getenv("EMBEDDING_DIM", 384),
            }
            self.config_collection.insert_one({"_id": "default", **self.config})
        
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
    
    def get_config(self):
        return self.config
        
    def update_config(self, config):
        updated_config = dict(self.config)
        updated_config.update(config)

        embedding_model_changed = False

        if self.config.get("embedding_model") != config.get("embedding_model"):
            parts = updated_config["embedding_model"].split("/")
            dir_name = parts[1] if len(parts) > 1 else parts[0]
            embdedding_dir = os.path.join("models", "embedding")
            config_file = os.path.join(embdedding_dir, dir_name, "config.json")
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    model_config = json.load(f)
                updated_config["embedding_dim"] = model_config.get("hidden_size")
            except:
                pass
            embedding_model_changed = True

        updated_config["_id"] = "default"

        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": updated_config},
            upsert=True
        )

        self.config = updated_config
        updated_config["embedding_model_changed"] = embedding_model_changed
        return updated_config

    def delete_all_chunks(self):
        try:
            self.chunks_collection.delete_many({})
            print("✅ All chunks deleted successfully.")
        except Exception as e:
            print(f"Error deleting chunks: {e}")