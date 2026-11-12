import os
import json
from groq import Groq


class InventoryAI:
    """Talks to the Groq API. The rest of the app works without it."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def is_configured(self):
        return bool(self.api_key) and "your_" not in self.api_key

    def _complete(self, system_prompt, user_prompt):
        if not self.is_configured():
            raise RuntimeError("AI is not configured. Add a real GROQ_API_KEY to your .env file and restart the app. Inventory tools still work.")
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_completion_tokens=4000,  # room for reasoning models too
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            raise RuntimeError("The model returned an empty answer. Try again.")
        return text

    def generate(self, mode, products, question=None):
        inventory_json = json.dumps(products, ensure_ascii=False)
        if mode == "analysis":
            prompt = "Review this inventory. Give a concise overview, risks, notable patterns, and practical next steps. Do not invent sales data or demand forecasts."
            user = f"Inventory records:\n{inventory_json}"
        elif mode == "reorder":
            prompt = ("Act as a careful inventory advisor. Identify low and out-of-stock items. "
                      "Suggest a practical reorder quantity only as an estimate, explain assumptions, "
                      "and state when more sales/lead-time data is needed. Do not claim certainty.")
            user = f"Inventory records:\n{inventory_json}"
        else:
            prompt = ("Answer the user's inventory question using only the supplied records. "
                      "Calculate totals when possible. If the data does not contain the answer, say so.")
            user = f"Inventory records:\n{inventory_json}\n\nQuestion: {question}"
        return self._complete(prompt, user)

    def generate_description(self, details):
        name = str(details.get("name", "")).strip()
        category = str(details.get("category", "")).strip()
        if not name or not category:
            raise ValueError("Enter a product name and category first.")
        prompt = "Write a clear, appealing, factual product description in 2-3 sentences. Do not invent specifications."
        user = (f"Product name: {name}\nCategory: {category}\n"
                f"Details: {details.get('details', '')}\nPrice: {details.get('price', 'not supplied')}")
        return self._complete(prompt, user)
