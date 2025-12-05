from sentence_transformers import SentenceTransformer
import numpy as np
import os

class EmbeddingService:
    def __init__(self, config):
        self.model = None
        self.current_model = None
        self.embdedding_dir = os.path.join("models", "embedding")
        self.embdedding_model = config["embedding_model"]
        self.load_model()
    
    def load_model(self):
        model_name = self.embdedding_model
        if self.current_model == model_name and self.model:
            return
        try:
            print(f"Loading EMBEDDING model {model_name}...")
            parts = model_name.split("/")
            dir_name = parts[1] if len(parts) > 1 else parts[0]
            model_dir = os.path.join(self.embdedding_dir, dir_name)
            self.model = SentenceTransformer(
                model_dir, 
                device='cpu'
            )
            self.current_model = model_name
            print(f"✅ Loaded EMBEDDING model {model_name} successfully!")
        except:
            self.model = None
            self.current_model = None

    def normalize(self, v):
        v = np.array(v)
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm
    
    def embed_text(self, text: str):
        
        if not self.model or not text:
            return None
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            embedding = self.normalize(embedding)
            return embedding.tolist()
        except:
            return None