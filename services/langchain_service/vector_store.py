from langchain_community.vectorstores import Milvus
from pymilvus import connections, utility

class VectorStore:
    def __init__(self, config, embedding_service):
        self.config = config
        self.embedding_service = embedding_service
        
        connections.connect(
            host=config.milvus_host,
            port=config.milvus_port
        )
        
        self.collection_name = "arabic_docs_langchain"
        
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
        
        self.vector_store = Milvus(
            embedding_function=embedding_service.model,
            collection_name=self.collection_name,
            connection_args={
                "host": config.milvus_host,
                "port": config.milvus_port
            },
            index_params={
                "metric_type": "COSINE",
                "index_type": "FLAT",
                "params": {}
            },
            search_params={"metric_type": "COSINE"},
            consistency_level="Strong"
        )
    
    def add_documents(self, documents, embeddings, chunk_ids):
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        for i, metadata in enumerate(metadatas):
            metadata["chunk_id"] = chunk_ids[i]
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def search(self, query_embedding, top_k):
        results = self.vector_store.similarity_search_with_score_by_vector(
            embedding=query_embedding,
            k=top_k
        )
        
        filtered_results = []
        for doc, score in results:
            if score >= self.config.similarity_threshold:
                filtered_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
        
        return filtered_results
    
    def delete_all(self):
        utility.drop_collection(self.collection_name)