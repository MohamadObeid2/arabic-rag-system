import os
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
from sentence_transformers import SentenceTransformer
import torch

def download_models():
    models_dir = "models"
    embedding_dir = os.path.join(models_dir, "embedding")
    llm_dir = os.path.join(models_dir, "llm")
    
    os.makedirs(embedding_dir, exist_ok=True)
    os.makedirs(llm_dir, exist_ok=True)
    
    print("Downloading embedding model...")
    try:
        embedding_model = SentenceTransformer('intfloat/multilingual-e5-base')
        embedding_model.save(embedding_dir)
        print(f"Embedding model saved to {embedding_dir}")
    except Exception as e:
        print(f"Error downloading embedding model: {e}")
    
    print("\nDownloading LLM model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
        model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2-1.5B-Instruct",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        tokenizer.save_pretrained(llm_dir)
        model.save_pretrained(llm_dir)
        print(f"LLM model saved to {llm_dir}")
    except Exception as e:
        print(f"Error downloading LLM model: {e}")
        print("Note: For smaller models, you might want to use:")
        print("Qwen/Qwen2-0.5B-Instruct or microsoft/phi-2")

if __name__ == "__main__":
    download_models()