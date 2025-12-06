from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
import os

class EmbeddingService:
    def __init__(self, config):
        self.config = config
        self.embdedding_model = config.embedding_model
        
        print(f"Loading EMBEDDING model {self.embdedding_model}...")

        self.model = HuggingFaceEmbeddings(
            model_name=self.embdedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        print(f"✅ Loaded EMBEDDING model {self.embdedding_model} successfully!")
    
    def embed_text(self, text):
        return self.model.embed_query(text)
    
    def embed_documents(self, documents):
        texts = [doc["content"] for doc in documents]
        return self.model.embed_documents(texts)