import ollama

class LLMService:
    def __init__(self, config):
        self.llm_model = config["llm_model"]
        self.temperature = 0.5

    def generate_response(self, prompt: str):
        res = ollama.chat(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": self.temperature}
        )
        return res["message"]["content"]
