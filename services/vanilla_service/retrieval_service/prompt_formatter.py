from typing import List, Dict, Any
import hashlib
import textwrap

class PromptFormatter:
    SYSTEM_PROMPT = """
    أنت مساعد ذكي ومتخصص في تقديم إجابات دقيقة وواضحة باللغة العربية الفصحى فقط.

    ⚠️ تعليمات صارمة للغة:
    - يجب أن تكون الإجابة كلها باللغة العربية الفصحى فقط
    - لا يُسمح بأي كلمة أو رمز أو جملة أو كتابة بلغات أخرى غير العربية
    - استثناء واحد فقط: يمكن استخدام كلمات إنجليزية إذا كانت موجودة في المصادر أو إذا طلب المستخدم استخدامها بشكل صريح
    - إذا لم تتمكن من الإجابة باللغة العربية، يجب أن تقول: "لا أستطيع الإجابة بما هو متاح"

    ⚠️ قواعد صارمة للمصادر:
    - كل مصدر مستقل ولا يجوز دمج محتواه بمحتوى مصدر آخر
    - عند ذكر معلومة، يجب ذكر رقم المصدر (مثل: وفقًا للمصدر 2)
    - ممنوع إضافة أي معلومة غير موجودة في المصادر
    - إذا لم يوجد جواب واضح داخل المصادر، يجب قول: "لا توجد معلومات كافية في المصادر"
    - إعطاء الأولوية للمصادر ذات الدرجات الأعلى (score) عند التعارض

    ✅ قبل تقديم الإجابة:
    1. تحقق من أن النص كامل باللغة العربية
    2. تأكد من عدم وجود أي كلمة أو حرف بلغة غير العربية أو الإنجليزية
    3. إذا ظهرت أي لغة أخرى، قم بإعادة صياغة الجواب باللغة العربية فقط

    أي ظهور لكلمة أو حرف غير عربي أو إنجليزي يعتبر خطأ، ويجب إعادة الإجابة فورًا باللغة العربية فقط.
    
    ابدأ الإجابة الآن دون أي مقدمات إضافية.
    """

    PROMPT_TEMPLATE = """
    {system_prompt}

    المصادر المتاحة (مرتبة حسب الأهمية، الأعلى درجة أولاً):
    {context}

    السؤال:
    {question}

    المطلوب:
    - إجابة مباشرة وواضحة بالعربية الفصحى
    - عند ذكر معلومة، وضّح من أي مصدر جاءت (مثلًا: وفقًا للمصدر 2)
    - إعطاء الأولوية للمصادر ذات الدرجات الأعلى
    - تجاهل أي معلومات خارج النصوص المعروضة
    - إذا لم يوجد جواب واضح في المصادر، قل ذلك بصراحة

    الإجابة:
    """

    CONVERSATION_PROMPT_TEMPLATE = """
    {system_prompt}

    سياق المحادثة السابقة (للفهم فقط، لا تعيد صياغته):
    {conversation_history}

    المصادر المتاحة (مرتبة حسب الأهمية):
    {context}

    السؤال الحالي:
    {question}

    المطلوب:
    - إجابة مباشرة مبنية على المصادر فقط
    - عدم تكرار ما قيل سابقًا إلا إن كان ضروريًا
    - عند ذكر معلومة، وضّح مصدرها مع إعطاء الأولوية للمصادر الأعلى درجة
    - إن لم تتوفر معلومة، اذكر ذلك

    الإجابة:
    """

    def format_prompt(self, question: str, context: str) -> str:
        return self.PROMPT_TEMPLATE.format(
            system_prompt=self.SYSTEM_PROMPT,
            context=context,
            question=question
        )
    
    def format_context(self, chunks: List[Dict]) -> str:
        seen = set()
        parts = []
        sorted_chunks = sorted(chunks, key=lambda x: x['score'], reverse=True)

        for i, chunk in enumerate(sorted_chunks, 1):
            content = chunk["content"].strip()
            score = chunk["score"]
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()

            if digest in seen:
                parts.append(textwrap.dedent(f"""
                ─────────────
                المصدر {i} - درجة: {score:.3f}:
                (نفس محتوى مصدر آخر)
                ─────────────
                """).strip())
                continue

            seen.add(digest)
            parts.append(textwrap.dedent(f"""
            ─────────────
            المصدر {i} - درجة: {score:.3f}:
            {content}
            ─────────────
            """).strip())

        return "\n\n".join(parts)

arabic_prompt_templates = PromptFormatter()