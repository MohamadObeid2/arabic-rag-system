class PromptUtils:
    def create_prompt(self, question: str, context: list[dict], top_k=3):
        if not context:
            return f"السؤال: {question}\n\nالإجابة:"

        context_text = ""
        for i, chunk in enumerate(context[:top_k]):
            text = chunk['content'][:512]
            context_text += f"المصدر {i+1}:\n{text}\n\n"

        prompt = f"""المهمة: أجب على السؤال التالي باستخدام المعلومات الواردة فقط في المصادر أدناه. لا تضف أي معلومات أخرى. أجب باللغة العربية بشكل مختصر ودقيق.

{context_text}

السؤال: {question}

الإجابة:"""

        return prompt