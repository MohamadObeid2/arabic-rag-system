from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class SystemConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    similarity_threshold: float = 0.3
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"