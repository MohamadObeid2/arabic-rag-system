from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import os
import numpy as np

class VectorStore:
    def __init__(self, config):
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.collection_name = "arabic_docs"
        self.connected = False
        self.collection = None
        self.dim = config["embedding_dim"]
        self.embedding_model = config["embedding_model"]
        self.top_k = config["top_k"]
        self.similarity_threshold = config["similarity_threshold"]
        self.connect()
    
    def connect(self):
        connections.connect(host=self.host, port=self.port)
        self.connected = True
        self.create_collection()
        self.collection.load()
    
    def create_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=500)
        ]
        schema = CollectionSchema(fields)
        self.collection = Collection(self.collection_name, schema)

        index_params = {
            "index_type": "FLAT",
            "metric_type": "COSINE",
            "params": {}
        }
        self.collection.create_index("vector", index_params)

    def reset_collection(self):
        if utility.has_collection(self.collection_name):
            Collection(self.collection_name).drop()
            self.create_collection()
            self.collection.load()

    def store_vectors(self, vectors, chunk_ids):
        vectors = [np.array(v, dtype=np.float32)/np.linalg.norm(v) for v in vectors]
        data = [vectors, chunk_ids]
        mr = self.collection.insert(data)
        return mr.primary_keys
        
    def search(self, query_vector, query_text=None):
        query_vector = np.array(query_vector, dtype=np.float32)
        query_vector /= np.linalg.norm(query_vector)
        search_params = {
            "metric_type": "COSINE",
            "params": {}
        }
        search_results = self.collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=self.top_k,
            output_fields=["chunk_id"]
        )
        
        results = []
        vectors = []
        for hit in search_results[0]:
            similarity = max(0.0, min(1.0, hit.distance))
            if similarity >= self.similarity_threshold:
                results.append({
                    "vector_id": str(hit.id),
                    "chunk_id": hit.entity.get("chunk_id"),
                    "score": float(similarity)
                })
                vectors.append(hit.entity.get("vector"))
        return results, vectors
    
    def get_all_vectors(self):
        results = self.collection.query(expr="id >= 0", output_fields=["chunk_id", "id", "vector"])
        
        vectors = []
        for result in results:
            vectors.append({
                "id": result.get("id"),
                "chunk_id": result.get("chunk_id"),
            })
        return vectors
    
    def delete_all_vectors(self):
        self.collection.delete(expr="id >= 0")
        self.collection.flush()
        print("✅ All vectors deleted successfully.")