import ollama
from .prompt_formatter import PromptFormatter

class LLMService:
    def __init__(self, config):
        self.llm_model = config["llm_model"]
        self.temperature = 0.5
        self.prompt_formatter = PromptFormatter()

    def generate_response(self, question: str, chunks):

        context = self.prompt_formatter.format_context(chunks)
        prompt = self.prompt_formatter.format_prompt(question, context)

        res = ollama.chat(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": self.temperature}
        )
        return res["message"]["content"]
