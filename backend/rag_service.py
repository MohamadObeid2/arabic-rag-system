from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .prompt_service import PromptService
from .llm_service import LLMService

class RAGService:
    def __init__(self):
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
        self.prompt_service = PromptService()
    
    def set_mongo_service(self, mongo_service):
        self.chunking_service.set_mongo_service(mongo_service)
    
    def insert(self, folder_path: str, config: dict):
        documents = self.chunking_service.load_text_files(folder_path)
        
        if not documents:
            return {"documents": 0, "chunks": 0, "message": "لم يتم العثور على مستندات"}
        
        total_chunks = 0
        for doc in documents:
            chunks = self.chunking_service.create_chunks(doc, config["chunk_size"], config["chunk_overlap"])
            
            if not chunks:
                continue
            
            chunk_ids = self.chunking_service.store_chunks(chunks)
            
            embeddings = []
            chunk_id_list = []
            
            for i, chunk in enumerate(chunks):
                embedding = self.embedding_service.embed_text(chunk["content"], config["embedding_model"])
                if embedding:
                    embeddings.append(embedding)
                    chunk_id_list.append(chunk_ids[i])
            
            if embeddings:
                vector_ids = self.vector_store.store_vectors(embeddings, chunk_id_list)
                
                for i, vector_id in enumerate(vector_ids):
                    if self.chunking_service.mongo_service:
                        self.chunking_service.mongo_service.chunks_collection.update_one(
                            {"_id": chunk_ids[i]},
                            {"$set": {"vector_id": vector_id}}
                        )
            
            total_chunks += len(chunks)
        
        return {
            "documents": len(documents),
            "chunks": total_chunks,
            "message": f"تمت العملية بنجاح"
        }
    
    def search(self, question: str, config: dict):
        if not question.strip():
            return {
                "answer": "يرجى كتابة سؤال",
                "sources": []
            }
        
        question_embedding = self.embedding_service.embed_text(question, config["embedding_model"])
        
        if not question_embedding:
            return {
                "answer": "تعذر معالجة السؤال",
                "sources": []
            }
        
        results = self.vector_store.search(
            question_embedding,
            config["top_k"],
            config["similarity_threshold"]
        )
        
        if not results:
            return {
                "answer": "لم أجد معلومات كافية للإجابة",
                "sources": []
            }
        
        vector_ids = [r["vector_id"] for r in results]
        chunks = self.chunking_service.mongo_service.get_chunks_by_vector_ids(vector_ids)
        
        prompt = self.prompt_service.create_prompt(question, chunks)
        answer = self.llm_service.generate_response(prompt, config["llm_model"])
        
        sources = []
        for i, chunk in enumerate(chunks):
            sources.append({
                "file": chunk["metadata"]["filename"],
                "content": chunk["content"][:150] + "..." if len(chunk["content"]) > 150 else chunk["content"],
                "score": results[i]["score"] if i < len(results) else 0.0
            })
        
        return {
            "answer": answer,
            "sources": sources
        }