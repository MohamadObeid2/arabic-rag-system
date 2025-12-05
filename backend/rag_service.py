from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .prompt_utils import PromptUtils
from .llm_service import LLMService
from bson import ObjectId

class RAGService:
    def __init__(self, config):
        self.prompt_utils = PromptUtils()
        self.chunking_service = ChunkingService(config)
        self.vector_store = VectorStore(config)
        self.embedding_service = EmbeddingService(config)
        self.llm_service = LLMService(config)
        self.mongo_client = None
    
    def set_mongo_client(self, mongo_client):
        self.mongo_client = mongo_client
    
    def insert(self, folder_path: str):
        documents = self.chunking_service.load_text_files(folder_path)
        
        try:
            if not documents:
                return {"documents": 0, "chunks": 0, "message": "لم يتم العثور على مستندات"}
            
            total_chunks = 0
            for doc in documents:
                chunks = self.chunking_service.create_chunks(doc)
                if not chunks:
                    continue
                
                chunk_ids = self.mongo_client.store_chunks(chunks)
                embeddings = []
                chunk_id_list = []
                
                for i, chunk in enumerate(chunks):
                    embedding = self.embedding_service.embed_text(chunk["content"])
                    
                    if embedding:
                        embeddings.append(embedding)
                        chunk_id_list.append(chunk_ids[i])
                        
                if embeddings:
                    vector_ids = self.vector_store.store_vectors(embeddings, chunk_id_list)
                    for i, vector_id in enumerate(vector_ids):
                        if self.mongo_client:
                            self.mongo_client.chunks_collection.update_one(
                                {"_id": ObjectId(chunk_ids[i])},
                                {"$set": {"vector_id": vector_id}}
                            )
                total_chunks += len(chunks)
            
            return {
                "documents": len(documents),
                "chunks": total_chunks,
                "message": f"تمت العملية بنجاح"
            }
        except Exception as e:
            print(e)
    
    def retrieve(self, question: str):
        if not question.strip():
            return {
                "answer": "يرجى كتابة سؤال",
                "sources": []
            }
        
        question_embedding = self.embedding_service.embed_text(question)

        if not question_embedding:
            return {
                "answer": "تعذر معالجة السؤال",
                "sources": []
            }
        
        results, vectors = self.vector_store.search(question_embedding)
        
        if not results:
            return {
                "answer": "لم أجد معلومات كافية للإجابة",
                "sources": []
            }
        
        chunks = self.mongo_client.get_chunks_by_vector_ids(results)
        prompt = self.prompt_utils.create_prompt(question, chunks)
        answer = self.llm_service.generate_response(prompt)
        
        sources = []
        for i, chunk in enumerate(chunks):
            sources.append({
                "file": chunk["metadata"]["filename"],
                "content": chunk["content"],
                "score": results[i]["score"] if i < len(results) else 0.0
            })
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def search(self, query: str):
        if not query.strip():
            return {
                "answer": "يرجى كتابة سؤال",
                "sources": []
            }
        
        query_embedding = self.embedding_service.embed_text(query)
        
        if not query_embedding:
            return []
        
        results, vectors = self.vector_store.search(query_embedding)
        
        if not results:
            return []
        
        chunks = self.mongo_client.get_chunks_by_vector_ids(results)

        return chunks