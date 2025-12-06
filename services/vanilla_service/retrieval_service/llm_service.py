from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import re

class LLMService:
    def __init__(self, config):
        self.tokenizer = None
        self.model = None
        self.llm_model = config["llm_model"]
        self.current_model = None
        self.llm_dir = os.path.join("models", "llm")
        self.temperature = 0.5
        self.do_sample = False

        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

        self.load_model()
    
    def load_model(self):
        model_name = self.llm_model
        if self.current_model == model_name and self.model:
            return
        
        parts = model_name.split("/")
        dir_name = parts[1] if len(parts) > 1 else parts[0]
        model_dir = os.path.join(self.llm_dir, dir_name)

        if not os.path.exists(model_dir):
            self.tokenizer = None
            self.model = None
            self.current_model = None
            return

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="auto",
            torch_dtype=torch.float16
        )

        self.current_model = model_name

    def generate_response(self, prompt: str):
        max_model_length = self.tokenizer.model_max_length
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_model_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            do_sample=self.do_sample,
            max_new_tokens=150,
            repetition_penalty=1.2,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_ids = outputs[:, inputs["input_ids"].shape[1]:]
        txt = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        txt = " ".join([line.strip() for line in txt.splitlines() if line.strip()])
        return txt