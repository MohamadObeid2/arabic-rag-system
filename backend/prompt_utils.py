class PromptUtils:
    def filter_context(self, question: str, context: list[dict]):
        q = question.strip().split()
        filtered = []
        for c in context:
            t = c["content"]
            if any(k in t for k in q):
                filtered.append(c)
        return filtered

    def create_prompt(self, question: str, context: list[dict], top_k=3):
        context = self.filter_context(question, context)
        if not context:
            return f"### السؤال:\n{question}\n\n### الإجابة (بناءً على المصادر فقط): لا تتوفر معلومات كافية."
        context_text = ""
        for i, c in enumerate(context[:top_k]):
            context_text += f"### المصدر {i+1}:\n{c['content']}\n\n"
        prompt = f"""أنت الآن في وضع RAG صارم. لا تمتلك أي معرفة خارج النصوص المزودة. أي معلومة ليست موجودة في المصادر يجب رفضها بالكامل.

### المصادر:
{context_text}
### السؤال:
{question}

### الإجابة (بناءً على المصادر فقط):
"""
        return prompt