import os
from pymongo import MongoClient

class Config:
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017")
        self.mongo_client = MongoClient(self.mongodb_uri)
        self.db = self.mongo_client.arabic_rag_langchain
        self.config_collection = self.db.system_config_langchain

        self.milvus_host = os.getenv("MILVUS_HOST", "localhost")
        self.milvus_port = os.getenv("MILVUS_PORT", 19530)

        self.config = self.get_config()
        if not self.config:
            self.config = {
                "_id": "default",
                "chunk_size": int(os.getenv("CHUNK_SIZE", 500)),
                "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", 50)),
                "top_k": int(os.getenv("TOP_K", 3)),
                "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", 0.5)),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base"),
                "llm_model": os.getenv("LLM_MODEL", "Qwen2-1.5B"),
                "milvus_host": os.getenv("MILVUS_HOST", "localhost"),
                "milvus_port": os.getenv("MILVUS_PORT", "19530")
            }
            self.config_collection.insert_one(self.config)

        self.chunk_size = self.config["chunk_size"]
        self.chunk_overlap = self.config["chunk_overlap"]
        self.top_k = self.config["top_k"]
        self.similarity_threshold = self.config["similarity_threshold"]
        self.embedding_model = self.config["embedding_model"]
        self.llm_model = self.config["llm_model"]

    def get_config(self):
        return self.config_collection.find_one({"_id": "default"})

    def update_config(self, config_data):
        updated_config = dict(self.config)
        updated_config.update(config_data)
        self.config_collection.update_one(
            {"_id": "default"},
            {"$set": updated_config},
            upsert=True
        )
        
        self.config.update(config_data)
        for key, value in config_data.items():
            setattr(self, key, value)
        return updated_config