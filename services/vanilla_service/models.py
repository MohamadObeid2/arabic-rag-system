from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class ConfigModel(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    similarity_threshold: float = 0.5
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "TinyLlama-1.1B-Chat-v1.0"
    embedding_dim: int = 384