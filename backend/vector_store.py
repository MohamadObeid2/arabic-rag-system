from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import os

class VectorStore:
    def __init__(self):
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.collection_name = "arabic_docs"
        self.dim = 384
        self.connected = False
        self.collection = None
        self._connect()
    
    def _connect(self):
        try:
            connections.connect(host=self.host, port=self.port)
            self.connected = True
            self._create_collection()
        except Exception as e:
            print(f"Milvus connection failed: {e}")
            self.connected = False
    
    def _create_collection(self):
        if not self.connected:
            return
        
        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                return
        except:
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
            "metric_type": "L2",
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
            self.collection.load()
            mr = self.collection.insert(data)
            self.collection.release()
            return mr.primary_keys
        except Exception as e:
            print(f"Store vectors error: {e}")
            return []
    
    def search(self, query_vector, top_k=5, threshold=0.3):
        if not self.connected or not query_vector:
            return []
        
        try:
            self.collection.load()
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["chunk_id"]
            )
            
            hits = []
            for hit in results[0]:
                if hit.score < threshold:
                    hits.append({
                        "vector_id": str(hit.id),
                        "chunk_id": hit.entity.get('chunk_id'),
                        "score": float(hit.score)
                    })
            
            self.collection.release()
            return hits
        except Exception as e:
            print(f"Search error: {e}")
            return []