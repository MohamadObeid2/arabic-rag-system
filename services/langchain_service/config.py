import os
from pymongo import MongoClient

class Config:
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017")
        self.milvus_host = os.getenv("MILVUS_HOST", "localhost")
        self.milvus_port = os.getenv("MILVUS_PORT", "19530")
        
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        self.top_k = int(os.getenv("TOP_K", "3"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
        
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.llm_model = os.getenv("LLM_MODEL", "TinyLlama-1.1B-Chat-v1.0")
        
        self.mongo_client = MongoClient(self.mongodb_uri)
        self.db = self.mongo_client.arabic_rag_langchain
        self.chunks_collection = self.db.chunks_langchain
        self.config_collection = self.db.system_config_langchain
        
        self.init_database()
    
    def init_database(self):
        if "system_config_langchain" not in self.db.list_collection_names():
            self.config_collection.insert_one({
                "_id": "default",
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "top_k": self.top_k,
                "similarity_threshold": self.similarity_threshold,
                "embedding_model": self.embedding_model,
                "llm_model": self.llm_model
            })
    
    def get_config(self):
        return self.config_collection.find_one({"_id": "default"})
    
    def update_config(self, config_data):
        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": config_data},
            upsert=True
        )
        return config_data