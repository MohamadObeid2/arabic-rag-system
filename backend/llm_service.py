from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

class LLMService:
    def __init__(self, config):
        self.tokenizer = None
        self.model = None
        self.llm_model = config["llm_model"]
        self.current_model = None
        self.llm_dir = os.path.join("models", "llm")
        self.load_model()
    
    def load_model(self):
        model_name = self.llm_model
        if self.current_model == model_name and self.model:
            return
        
        print(f"Loading LLM model {model_name}...")
        parts = model_name.split("/")
        dir_name = parts[1] if len(parts) > 1 else parts[0]
        model_dir = os.path.join(self.llm_dir, dir_name)

        if not os.path.exists(model_dir):
            print(f"Model directory {model_dir} does not exist!")
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
        print(f"✅ Loaded LLM model {model_name} successfully!")

    def generate_response(self, prompt: str):
        if not self.tokenizer or not self.model:
            return "النموذج غير جاهز للاستخدام"

        try:
            max_model_length = self.tokenizer.model_max_length
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=max_model_length
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids.to(self.model.device),
                    attention_mask=inputs.attention_mask.to(self.model.device),
                    temperature=0.5,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            txt = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "### الإجابة (بناءً على المصادر فقط):" in txt:
                return txt.split("### الإجابة (بناءً على المصادر فقط):")[-1].strip()
            
            return txt
        except Exception as e:
            print(e)
            return "حدث خطأ أثناء توليد الإجابة"