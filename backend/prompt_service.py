class PromptService:
    def create_prompt(self, question: str, context: list[dict]):
        if not context:
            return f"السؤال: {question}\n\nالإجابة:"
        
        context_text = ""
        for i, chunk in enumerate(context):
            context_text += f"المصدر {i+1}:\n{chunk['content']}\n\n"
        
        prompt = f"""باستخدام المعلومات التالية، أجب على السؤال التالي باللغة العربية:

{context_text}

السؤال: {question}

الإجابة بناءً على المعلومات أعلاه:"""
        
        return prompt