from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import os
import json

class VectorStore:
    def __init__(self, config):
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.collection_name = "arabic_docs"
        self.connected = False
        self.collection = None
        self.loaded = False
        self.embdedding_dir = os.path.join("models", "embedding")
        self.dim = config["embedding_dim"]
        self.embedding_model = config["embedding_model"]
        self.top_k = config["top_k"]
        self.similarity_threshold = config["similarity_threshold"]
        self.connect()
    
    def connect(self):
        try:
            connections.connect(host=self.host, port=self.port)
            self.connected = True
            self.create_collection()
            self.collection.load()
        except Exception as e:
            print(f"Milvus connection failed: {e}")
            self.connected = False
    
    def create_collection(self):
        if not self.connected:
            return

        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                return
        except Exception:
            pass
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=500)
        ]

        schema = CollectionSchema(fields)
        self.collection = Collection(self.collection_name, schema)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
        self.collection.create_index("vector", index_params)

    def store_vectors(self, vectors, chunk_ids):
        if not self.connected or not vectors:
            return []
        
        data = [
            vectors,
            chunk_ids
        ]
        
        try:
            mr = self.collection.insert(data)
            return mr.primary_keys
        except Exception as e:
            print(f"Store vectors error: {e}")
            return []
        
    def search(self, query_vector):
        if not self.connected or not query_vector:
            return []

        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }

            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=self.top_k,
                output_fields=["chunk_id"]
            )

            hits = []
            for hit in results[0]:
                similarity = 1 - hit.distance
                similarity = max(0.0, min(1.0, similarity))
                if similarity >= self.similarity_threshold:
                    hits.append({
                        "vector_id": str(hit.id),
                        "chunk_id": hit.entity.get("chunk_id"),
                        "score": float(similarity)
                    })

            return hits

        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_all_vectors(self):
        if not self.connected:
            return []
        results = self.collection.query(expr="id >= 0", output_fields=["chunk_id", "id"])
        vectors = []
        for result in results:
            vectors.append({
                "id": result.get("id"),
                "chunk_id": result.get("chunk_id")
            })
        
        return vectors
    
    def delete_all_vectors(self):
        if not self.connected:
            print("Not connected to Milvus.")
            return
        
        try:
            self.collection.delete(expr="id >= 0")
            self.collection.flush()
            print("✅ All vectors deleted successfully.")
        except Exception as e:
            print(f"Error deleting vectors: {e}")