from ..shared_services.embedding_service import EmbeddingService
from ..shared_services.vector_store import VectorStore
from .llm_service import LLMService
from .prompt_formatter import PromptFormatter

class RetrievalService:
    def __init__(self, config):
        self.vector_store = VectorStore(config)
        self.embedding_service = EmbeddingService(config)
        self.llm_service = LLMService(config)
        self.mongo_client = None
        self.prompt_formatter = PromptFormatter()
    
    def set_mongo_client(self, mongo_client):
        self.mongo_client = mongo_client
    
    def chat(self, question: str):
        if not question.strip():
            return {
                "question": question,
                "answer": "يرجى كتابة سؤال",
                "sources": []
            }
        
        question_embedding = self.embedding_service.embed_text(question)

        if not question_embedding:
            return {
                "question": question,
                "answer": "تعذر معالجة السؤال",
                "sources": []
            }
        
        results, vectors = self.vector_store.search(question_embedding)
        
        if not results:
            return {
                "question": question,
                "answer": "لم أجد معلومات كافية للإجابة",
                "sources": []
            }
        
        chunks = self.mongo_client.get_chunks_by_vector_ids(results)
        context = self.prompt_formatter.format_context(chunks)
        prompt = self.prompt_formatter.format_prompt(question, context)
        answer = self.llm_service.generate_response(prompt)
        
        sources = []
        for i, chunk in enumerate(chunks):
            sources.append({
                "file": chunk["metadata"]["filename"],
                "content": chunk["content"],
                "score": results[i]["score"] if i < len(results) else 0.0
            })
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }
    
    def search(self, query: str):
        if not query.strip():
            return {
                "success": False,
                "sources": []
            }
        
        query_embedding = self.embedding_service.embed_text(query)
        if not query_embedding:
            return {
                "success": True,
                "sources": []
            }
        
        results, vectors = self.vector_store.search(query_embedding)
        if not results:
            return {
                "success": True,
                "query": query,
                "sources": []
            }
        
        sources = self.mongo_client.get_chunks_by_vector_ids(results)
        
        return {
            "success": True,
            "query": query,
            "sources": sources
        }