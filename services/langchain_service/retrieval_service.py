from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
from pymilvus import connections

class RetrievalService:
    def __init__(self, config):
        self.config = config
        self.embdedding_model = config.embedding_model
        
        self.model = HuggingFaceEmbeddings(
            model_name=self.embdedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        connections.connect(
            host=config.milvus_host,
            port=config.milvus_port
        )
        
        self.collection_name = "arabic_docs_langchain"
        self.init_vector_store()
        self.init_llm()
        
        self.prompt_template = """السياق:
{context}

السؤال: {question}

الإجابة:"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def init_vector_store(self):
        from langchain_community.vectorstores import Milvus
        self.vector_store = Milvus(
            embedding_function=self.model,
            collection_name=self.collection_name,
            connection_args={
                "host": self.config.milvus_host,
                "port": self.config.milvus_port
            },
            auto_id=True
        )

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
            max_new_tokens=150,
            temperature=0.5,
            repetition_penalty=1.2
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)

    def embed_text(self, text):
        return self.model.embed_query(text)

    def search(self, query_embedding, top_k):
        results = self.vector_store.similarity_search_with_score_by_vector(
            embedding=query_embedding,
            k=top_k
        )

        filtered_results = []
        for doc, score in results:
            similarity = 1 - score
            if similarity >= self.config.similarity_threshold:
                filtered_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(similarity)
                })
        
        return filtered_results

    def chat(self, question):
        query_embedding = self.embed_text(question)
        results = self.search(query_embedding, self.config.top_k)
        
        if len(results) == 0:
            return {
                "question": question,
                "answer": "لا تتوفر معلومات كافية",
                "sources": []
            }
        
        context = ""
        for result in results:
            context += f"{result['content']}\n"
        
        prompt_text = self.prompt.format(context=context, question=question)
        answer = self.llm.invoke(prompt_text)
        
        return {
            "question": question,
            "answer": answer,
            "sources": results,
        }