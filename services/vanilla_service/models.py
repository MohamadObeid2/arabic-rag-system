from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class ConfigModel(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    similarity_threshold: float = 0.5
    embedding_model: str = "multilingual-e5-base"
    llm_model: str = "qwen2:7b"