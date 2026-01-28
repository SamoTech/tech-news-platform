# modules/writer/article_builder.py

import os
import time
import requests
from datetime import datetime
from typing import List, Dict

from modules.writer.angles import choose_angle
from modules.writer.memory import ArticleMemory
from modules.writer.templates import render_article
from modules.writer.rules_engine import ArticleRules
from modules.writer.authors import select_author


class ContentGenerator:
    """
    Generate high-quality articles using Google Gemini (FREE with rate limiting).
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def generate_section(
        self,
        section_name: str,
        items: List[Dict],
        angle: str,
        word_target: int = 150
    ) -> str:
        """
        Generate a single article section with real analysis.
        """

        sources_context = self._build_sources_context(items)

        system_prompt = """You are an expert technology journalist and analyst.
Write clear, insightful, specific content.
Avoid generic business jargon and repetitive phrases.
Focus on facts, technical details, and strategic implications.
Write in a professional, analytical tone."""

        prompts = {
            "introduction": f"""{system_prompt}

Write a compelling introduction for a tech news article.

EDITORIAL ANGLE: {angle}
NEWS SOURCES:
{sources_context}

REQUIREMENTS:
- {word_target} words minimum
- Hook the reader immediately with the most important development
- Mention specific companies, products, or technologies
- Explain why this matters NOW
- Be concrete, not generic
- NO phrases like "Recent developments indicate" or "In today's world"

Write ONLY the introduction paragraph. No labels, no titles.""",

            "analysis": f"""{system_prompt}

Provide deep technical and strategic analysis.

EDITORIAL ANGLE: {angle}
NEWS SOURCES:
{sources_context}

REQUIREMENTS:
- {word_target} words minimum
- Compare and contrast different sources
- Identify technical patterns and strategic decisions
- Discuss implementation details and architecture
- Include specific examples and data points
- Show technical expertise

Write ONLY the analysis paragraph. No labels, no titles.""",

            "implications": f"""{system_prompt}

Analyze the broader implications of these developments.

EDITORIAL ANGLE: {angle}
NEWS SOURCES:
{sources_context}

REQUIREMENTS:
- {word_target} words minimum
- WHO is affected: companies, users, developers, competitors
- HOW they're affected: market dynamics, product strategies
- Be concrete and actionable
- Include specific business implications
- Mention specific stakeholders by name

Write ONLY the implications paragraph. No labels, no titles.""",

            "key_takeaways": f"""{system_prompt}

Synthesize 3-4 key takeaways readers should remember.

EDITORIAL ANGLE: {angle}
NEWS SOURCES:
{sources_context}

REQUIREMENTS:
- {word_target} words minimum
- 3-4 distinct insights (not a list)
- Each insight must be unique and non-overlapping
- Strategic clarity and actionable understanding
- Avoid generic business speak
- Write as flowing paragraphs, not bullet points

Write ONLY the key takeaways paragraph. No labels, no titles.""",

            "conclusion": f"""{system_prompt}

Write a forward-looking conclusion.

EDITORIAL ANGLE: {angle}
NEWS SOURCES:
{sources_context}

REQUIREMENTS:
- {word_target} words minimum
- Future outlook and strategic direction
- What this signals about industry evolution
- Final insight that ties everything together
- Strong, memorable closing
- Do NOT repeat earlier sections

Write ONLY the conclusion paragraph. No labels, no titles."""
        }

        prompt = prompts.get(section_name, prompts["analysis"])
        return self._call_gemini(prompt)

    def _build_sources_context(self, items: List[Dict]) -> str:
        """Build context from source articles."""
        context = []
        for i, item in enumerate(items[:5], 1):
            context.append(f"""
Source {i}:
Title: {item.get('title', 'N/A')}
Summary: {item.get('summary', 'N/A')[:400]}
Authority: {item.get('source_authority', 0.5)}
Category: {item.get('category', 'N/A')}
""")
        return "\n".join(context)

    def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call Google Gemini API with rate limiting.
        """
        
        url = f"{self.endpoint}?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 800,
            }
        }

        for attempt in range(max_retries):
            try:
                # RATE LIMITING: Wait 5 seconds between requests
                if attempt > 0:
                    print(f"  Retry {attempt}/{max_retries}...")
                time.sleep(10)  # Respect Gemini free tier limits (6 requests/min max)
                
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract text from Gemini response
                if "candidates" in data and len(data["candidates"]) > 0:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    content = content.strip()
                    return content
                else:
                    raise RuntimeError("No content in Gemini response")

            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Gemini API failed after {max_retries} attempts: {e}")
                print(f"  Error: {e}, retrying...")
                continue

        return ""


def build_article(items: List[Dict]) -> Dict[str, str]:
    """
    Build a complete, high-quality article from news sources.
    """
    if not items:
        raise ValueError("No items provided")

    rules = ArticleRules()
    memory = ArticleMemory()
    generator = ContentGenerator()

    # Select editorial angle
    angle = choose_angle(items)

    # Generate title from primary source
    primary_title = items[0].get("title", "Tech Industry Update")
    
    # Select author
    author = select_author(
        title=primary_title,
        angle=angle,
        used_authors=memory.recent_authors(),
        allow_extended=True,
    )

    # Generate each section with rate limiting
    print("Generating introduction...")
    sections = {
        "introduction": generator.generate_section("introduction", items, angle, 150),
    }
    
    print("Generating analysis...")
    sections["analysis"] = generator.generate_section("analysis", items, angle, 180)
    
    print("Generating implications...")
    sections["implications"] = generator.generate_section("implications", items, angle, 150)
    
    print("Generating key takeaways...")
    sections["key_takeaways"] = generator.generate_section("key_takeaways", items, angle, 120)
    
    print("Generating conclusion...")
    sections["conclusion"] = generator.generate_section("conclusion", items, angle, 100)

    # Render article
    article_html = render_article(
        title=primary_title,
        sections=sections,
        angle=angle,
        author=f"{author['name']} — {author['role']}",
        date=datetime.utcnow().strftime("%B %d, %Y"),
    )

    # Validate
    violations = rules.validate_article(article_html)
    if violations:
        print(f"WARNING: Article has violations: {violations}")

    # Create meta description
    meta_desc = sections["introduction"][:160].rsplit(" ", 1)[0] + "..."

    # Remember this article
    memory.remember(
        title=primary_title,
        angle=angle,
        author=author["name"],
    )

    # Calculate word count
    word_count = len(article_html.split())

    return {
        "title": primary_title,
        "content": article_html,
        "meta_description": meta_desc,
        "angle": angle,
        "word_count": word_count,
        "source_titles": [item.get("title") for item in items[:3]],
    }
