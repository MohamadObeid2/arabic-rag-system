import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import torch

def download_small_models():
    models_dir = "models"
    embedding_dir = os.path.join(models_dir, "embedding")
    llm_dir = os.path.join(models_dir, "llm")
    
    os.makedirs(embedding_dir, exist_ok=True)
    os.makedirs(llm_dir, exist_ok=True)
    
    print("Downloading smaller embedding model...")
    try:
        embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        embedding_model.save(embedding_dir)
        print(f"Embedding model saved to {embedding_dir}")
    except Exception as e:
        print(f"Error downloading embedding model: {e}")
    
    print("\nDownloading smaller LLM model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        model = AutoModelForCausalLM.from_pretrained(
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        tokenizer.save_pretrained(llm_dir)
        model.save_pretrained(llm_dir)
        print(f"LLM model saved to {llm_dir}")
    except Exception as e:
        print(f"Error downloading LLM model: {e}")

if __name__ == "__main__":
    download_small_models()