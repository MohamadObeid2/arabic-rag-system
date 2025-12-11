from openai import OpenAI
from .prompt_formatter import PromptFormatter
import os

class LLMService:
    def __init__(self, config):
        self.llm_model = config["llm_model"]
        self.llm_dir = os.path.join("models", "llm")
        parts = self.llm_model.split("/")
        dir_name = parts[1] if len(parts) > 1 else parts[0]
        self.model_dir = os.path.join(self.llm_dir, dir_name)
        self.temperature = 0.5
        self.prompt_formatter = PromptFormatter()

        self.client = OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="EMPTY"
        )

    def generate_response(self, question: str, chunks):

        context = self.prompt_formatter.format_context(chunks)
        prompt = self.prompt_formatter.format_prompt(question, context)

        response = self.client.chat.completions.create(
            model=self.model_dir,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
        )

        return response.choices[0].message.content
