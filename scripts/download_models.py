import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

def download_models():
    models_dir = "models"
    llm_dir = os.path.join(models_dir, "llm", "Qwen2-7B")

    os.makedirs(llm_dir, exist_ok=True)

    print("\nDownloading LLM model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen2-7B",
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2-7B",
            dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )

        tokenizer.save_pretrained(llm_dir)
        model.save_pretrained(llm_dir)
        print(f"LLM model saved to {llm_dir}")
    except Exception as e:
        print(f"Error downloading LLM model: {e}")

if __name__ == "__main__":
    download_models()