# modules/writer/rewriter.py

import os
import requests
from typing import Dict


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"


class ArticleRewriter:
    """
    Lightweight, cost-efficient article rewriter using OpenRouter.
    Designed to REMOVE repetition and improve flow,
    not summarize or reduce length.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")

    def rewrite_sections(self, sections: Dict[str, str], angle: str) -> Dict[str, str]:
        rewritten = {}

        for name, text in sections.items():
            rewritten[name] = self._rewrite_text(
                section_name=name,
                text=text,
                angle=angle,
            )

        return rewritten

    def _rewrite_text(self, section_name: str, text: str, angle: str) -> str:
        prompt = (
            "You are a professional technology editor.\n"
            "Rewrite the following section to remove repetition, improve clarity, "
            "and enhance flow.\n"
            "Do NOT summarize.\n"
            "Do NOT reduce length.\n"
            "Preserve the original meaning and analytical tone.\n\n"
            f"Editorial angle: {angle}\n"
            f"Section: {section_name}\n\n"
            f"Text:\n{text}"
        )

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You rewrite text without shortening it."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.35,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            OPENROUTER_API_URL,
            json=payload,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
