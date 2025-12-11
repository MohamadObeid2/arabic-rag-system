from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from pymilvus import connections
import torch

class SearchService:
    def __init__(self, config):
        self.config = config
        self.embdedding_model = config.embedding_model
        device = self.get_best_device()
        self.model = HuggingFaceEmbeddings(
            model_name=self.embdedding_model,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True}
        )
        connections.connect(host=config.milvus_host, port=config.milvus_port)
        self.collection_name = "arabic_docs_langchain"
        self.init_vector_store()

    def init_vector_store(self):
        self.vector_store = Milvus(
            embedding_function=self.model,
            collection_name=self.collection_name,
            connection_args={"host": self.config.milvus_host, "port": self.config.milvus_port},
            auto_id=True
        )

    def embed_text(self, text):
        return self.model.embed_query(text)

    def search(self, query_embedding, top_k):
        results = self.vector_store.similarity_search_with_score_by_vector(
            embedding=query_embedding,
            k=top_k
        )
        filtered_results = []
        for doc, score in results:
            similarity = 1 - score
            if similarity >= self.config.similarity_threshold:
                filtered_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(similarity)
                })
        return filtered_results

    def get_best_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"