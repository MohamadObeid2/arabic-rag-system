from .chunking_service import ChunkingService
from ..shared_services.embedding_service import EmbeddingService
from ..shared_services.vector_store import VectorStore
from bson import ObjectId

class InsertionService:
    def __init__(self, config):
        self.chunking_service = ChunkingService(config)
        self.vector_store = VectorStore(config)
        self.embedding_service = EmbeddingService(config)
        self.mongo_client = None
    
    def set_mongo_client(self, mongo_client):
        self.mongo_client = mongo_client
    
    def insert(self, folder_path: str):
        documents = self.chunking_service.load_text_files(folder_path)
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
                vector_ids = self.vector_store.store(embeddings, chunk_id_list)
                for i, vector_id in enumerate(vector_ids):
                    self.mongo_client.chunks_collection.update_one(
                        {"_id": ObjectId(chunk_id_list[i])},
                        {"$set": {"vector_id": vector_id}}
                    )
            total_chunks += len(chunks)
        
        return {
            "documents": len(documents),
            "chunks": total_chunks,
            "message": "تمت العملية بنجاح"
        }