import os
import requests

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"


class ArticleRewriter:
    def __init__(self, model: str = "mistralai/mistral-7b-instruct"):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        self.model = model

    def rewrite(self, html_content: str) -> str:
        prompt = (
            "Rewrite the following HTML article to remove repetition, "
            "improve clarity, and keep SEO-friendly structure. "
            "Preserve headings, HTML tags, and overall meaning. "
            "Do NOT summarize. Do NOT shorten excessively.\n\n"
            f"{html_content}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/SamoTech/tech-news-platform",
            "X-Title": "tech-news-platform",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
        }

        resp = requests.post(OPENROUTER_API, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        return data["choices"][0]["message"]["content"]
