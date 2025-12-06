from langchain_core.prompts import PromptTemplate

class RAGService:
    def __init__(self, config, vector_store, llm_service):
        self.config = config
        self.vector_store = vector_store
        self.llm_service = llm_service
        
        self.prompt_template = """
أنت نظام RAG صارم جدًا. أجب فقط باستخدام المصادر المزوّدة.

المصادر:
{context}

السؤال: {question}

الإجابة:
"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def chat(self, question):
        query_embedding = self.vector_store.embedding_service.embed_text(question)
        
        results = self.vector_store.search(query_embedding, self.config.top_k)
        
        if not results:
            return {
                "question": question,
                "answer": "لا تتوفر معلومات كافية في المصادر.",
                "sources": []
            }
        
        context = ""
        sources = []
        for i, result in enumerate(results):
            context += f"المصدر {i+1}: {result['content']}\n"
            sources.append({
                "file": result["metadata"]["filename"],
                "content": result["content"],
                "score": result["score"]
            })
        
        prompt_text = self.prompt.format(context=context, question=question)
        answer = self.llm_service.generate(prompt_text)
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }
    
    def search_documents(self, query):
        query_embedding = self.vector_store.embedding_service.embed_text(query)
        
        results = self.vector_store.search(query_embedding, self.config.top_k)
        
        return {
            "query": query,
            "sources": results
        }