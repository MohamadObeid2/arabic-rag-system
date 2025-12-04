import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

def download_models():
    models_dir = "models"
    embedding_dir = os.path.join(models_dir, "embedding", "multilingual-e5-base")
    llm_dir = os.path.join(models_dir, "llm", "Qwen2-1.5B-Instruct")

    os.makedirs(embedding_dir, exist_ok=True)
    os.makedirs(llm_dir, exist_ok=True)

    print("Downloading embedding model...")
    try:
        embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")
        embedding_model.save(embedding_dir)
        print(f"Embedding model saved to {embedding_dir}")
    except Exception as e:
        print(f"Error downloading embedding model: {e}")

    print("\nDownloading LLM model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen2-1.5B-Instruct",
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2-1.5B-Instruct",
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )

        tokenizer.save_pretrained(llm_dir)
        model.save_pretrained(llm_dir)
        print(f"LLM model saved to {llm_dir}")
    except Exception as e:
        print(f"Error downloading LLM model: {e}")
        print("Tip: For smaller models, try 'Qwen/Qwen2-0.5B-Instruct' or 'microsoft/phi-2'")

if __name__ == "__main__":
    download_models()