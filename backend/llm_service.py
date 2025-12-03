from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class LLMService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.current_model = None
    
    def load_model(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        if self.current_model == model_name and self.model:
            return
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.current_model = model_name
        except:
            self.tokenizer = None
            self.model = None
            self.current_model = None
    
    def generate_response(self, prompt: str, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        if not self.model or self.current_model != model_name:
            self.load_model(model_name)
        
        if not self.tokenizer or not self.model:
            return "النموذج غير جاهز للاستخدام"
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids.to(self.model.device),
                    max_length=600,
                    temperature=0.7,
                    do_sample=True
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = response[len(prompt):].strip()
            
            if not answer:
                return "لم أستطع توليد إجابة مناسبة"
            
            return answer
        
        except Exception as e:
            return f"حدث خطأ أثناء توليد الإجابة"