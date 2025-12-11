from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from .search_service import SearchService
import torch
import os

class ChatService:
    def __init__(self, config, search_service: SearchService):
        self.config = config
        self.search_service = search_service
        self.init_llm()

    def init_llm(self):
        model_name = self.config.llm_model
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
            max_new_tokens=100,
            temperature=0.7,
            repetition_penalty=1.2
        )
        self.llm = HuggingFacePipeline(pipeline=pipe)

    def chat(self, question):
        query_embedding = self.search_service.embed_text(question)
        results = self.search_service.search(query_embedding, self.config.top_k)

        if not results:
            return {"question": question, "answer": "لا تتوفر معلومات كافية", "sources": []}

        docs = [Document(page_content=r["content"], metadata=r["metadata"]) for r in results]
        prompt = PromptTemplate.from_template(
            "استخدم المعلومات التالية للإجابة على السؤال:\n\n{context}\n\nالسؤال: {question}\n\nالإجابة:"
        )
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = self.llm.invoke(prompt.format(context=context, question=question))

        return {"question": question, "answer": answer, "sources": results}