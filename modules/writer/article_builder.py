# modules/writer/article_builder.py

import os
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
    Generate high-quality, original articles using LLM with actual source content.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")

        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        # Use a stronger model for better content
        self.model = "anthropic/claude-3.5-sonnet"

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

        # Build context from actual news items
        sources_context = self._build_sources_context(items)

        prompts = {
            "introduction": f"""Write a compelling introduction for a tech news article.

ANGLE: {angle}
NEWS SOURCES:
{sources_context}

Requirements:
- {word_target} words minimum
- Hook the reader immediately
- Mention the key development concretely
- Set up the analysis to follow
- Be specific, not generic
- NO phrases like "Recent developments indicate" or "In today's world"

Write only the paragraph content, no labels.""",

            "analysis": f"""Provide deep technical and strategic analysis of these developments.

ANGLE: {angle}
NEWS SOURCES:
{sources_context}

Requirements:
- {word_target} words minimum
- Compare and contrast the different sources
- Identify patterns and connections
- Discuss technical implications
- Be specific with examples
- Show expertise and insight

Write only the paragraph content, no labels.""",

            "implications": f"""Analyze the broader implications of these developments.

ANGLE: {angle}
NEWS SOURCES:
{sources_context}

Requirements:
- {word_target} words minimum
- Who is affected and how?
- Market/industry impact
- User/developer consequences
- Competitive dynamics
- Be concrete and actionable

Write only the paragraph content, no labels.""",

            "key_takeaways": f"""Synthesize the key takeaways readers should remember.

ANGLE: {angle}
NEWS SOURCES:
{sources_context}

Requirements:
- {word_target} words minimum
- 3-4 distinct insights
- Actionable understanding
- Strategic clarity
- Avoid generic business speak

Write only the paragraph content, no labels.""",

            "conclusion": f"""Write a forward-looking conclusion that ties everything together.

ANGLE: {angle}
NEWS SOURCES:
{sources_context}

Requirements:
- {word_target} words minimum
- Synthesize the main thread
- Future outlook
- Final strategic insight
- Strong closing

Write only the paragraph content, no labels."""
        }

        prompt = prompts.get(section_name, prompts["analysis"])

        return self._call_llm(prompt)

    def _build_sources_context(self, items: List[Dict]) -> str:
        """
        Build a structured context from source articles.
        """
        context = []
        for i, item in enumerate(items[:5], 1):
            context.append(f"""
Source {i}:
Title: {item.get('title', 'N/A')}
Summary: {item.get('summary', 'N/A')[:300]}
Authority: {item.get('source_authority', 0.5)}
Category: {item.get('category', 'N/A')}
""")
        return "\n".join(context)

    def _call_llm(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call OpenRouter API with retry logic.
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technology journalist and analyst. Write clear, insightful, specific content. Avoid generic business jargon and repetitive phrases."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(max_retries):
            try:
                r = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                r.raise_for_status()
                
                content = r.json()["choices"][0]["message"]["content"].strip()
                
                # Clean up any potential labels or formatting
                content = content.replace("Introduction:", "").replace("Analysis:", "")
                content = content.replace("Implications:", "").replace("Conclusion:", "")
                content = content.strip()
                
                return content

            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM API failed after {max_retries} attempts: {e}")
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

    # Generate each section with real content
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
        # Don't raise - let validator decide

    # Create meta description from introduction
    meta_desc = sections["introduction"][:160].rsplit(" ", 1)[0] + "..."

    # Remember this article
    memory.remember(
        title=primary_title,
        angle=angle,
        author=author["name"],
    )

    # Calculate final word count
    word_count = len(article_html.split())

    return {
        "title": primary_title,
        "content": article_html,
        "meta_description": meta_desc,
        "angle": angle,
        "word_count": word_count,
        "source_titles": [item.get("title") for item in items[:3]],
    }
