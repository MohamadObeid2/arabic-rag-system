class PromptUtils:
    def filter_context(self, question: str, context: list[dict], min_score=0.4):
        q = question.strip().split()
        filtered = []
        for c in context:
            t = c["content"]
            score = c.get("score", 0)
            if score >= min_score and any(k in t for k in q):
                filtered.append(c)
        return filtered

    def create_prompt(self, question: str, context: list[dict]):
        context = self.filter_context(question, context)
        
        if not context:
            return f"السؤال: {question}\n\nالإجابة: لا تتوفر معلومات كافية في المصادر."

        context_text = ""
        for i, c in enumerate(context):
            score = c.get("score", 0)
            context_text += f"المصدر {i+1} (score: {score:.2f}): {c['content']}\n"

        prompt = f"""
أنت نظام RAG صارم جدًا. أجب فقط باستخدام المصادر المزوّدة. لا تستخدم أي معرفة خارج هذه المصادر. لا تضيف أي تعليق أو تفسير أو نص إضافي. لا تخترع أي مصادر أو أسئلة جديدة.

السؤال: {question}

المصادر:
{context_text}

التعليمات:
- اعطِ إجابة دقيقة قصيرة (جملة أو جملتين فقط)
- يجب أن تذكر دائمًا المصدر الذي استندت إليه في الإجابة مثل "المصدر 1"
- إذا لم يذكر المصدر المعلومة، قل مباشرة: "لا يوجد في المصادر"
- لا تضف أي رموز أو نصوص إضافية أخرى
- لا تضف أي معلومات عندك، اكتف بالمعلومات المزودة حصرا

الإجابة:
"""
        return prompt