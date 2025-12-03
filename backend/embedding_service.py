from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        self.model = None
        self.current_model = None
    
    def load_model(self, model_name: str = "all-MiniLM-L6-v2"):
        if self.current_model == model_name and self.model:
            return
        
        try:
            self.model = SentenceTransformer(model_name, device='cpu')
            self.current_model = model_name
        except:
            self.model = None
            self.current_model = None
    
    def embed_text(self, text: str, model_name: str = "all-MiniLM-L6-v2"):
        if not self.model or self.current_model != model_name:
            self.load_model(model_name)
        
        if not self.model or not text:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except:
            return None