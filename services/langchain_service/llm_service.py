from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os

class LLMService:
    def __init__(self, config):
        self.config = config

        model_name = config.llm_model
        print(f"Loading LLM model {model_name}...")

        self.llm_dir = os.path.join("models", "llm")
        parts = model_name.split("/")
        dir_name = parts[1] if len(parts) > 1 else parts[0]
        model_dir = os.path.join(self.llm_dir, dir_name)

        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=150,
            temperature=0.5,
            repetition_penalty=1.2
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)
        print(f"✅ Loaded LLM model {model_name} successfully!")
    
    def generate(self, prompt):
        return self.llm.invoke(prompt)