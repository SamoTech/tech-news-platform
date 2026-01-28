# modules/writer/article_builder.py

import os
import re
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

        # Using gemini-1.5-flash-8b for higher rate limits
        # Alternative: gemini-2.0-flash or gemini-1.5-flash
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent"

    def generate_full_article(self, items: List[Dict], angle: str) -> Dict[str, str]:
        """
        Generate entire article in ONE API call to avoid rate limiting.
        This is much more efficient than 5 separate calls.
        """
        
        sources_context = self._build_sources_context(items)
        
        system_prompt = """You are an expert technology journalist and analyst.
Write clear, insightful, specific content.
Avoid generic business jargon and repetitive phrases.
Focus on facts, technical details, and strategic implications.
Write in a professional, analytical tone."""
        
        prompt = f"""{system_prompt}

Write a complete tech news article with the following structure.

EDITORIAL ANGLE: {angle}

NEWS SOURCES:
{sources_context}

Generate the article with these 5 sections. Label each section clearly with its number and name:

1. INTRODUCTION (150+ words):
   - Hook readers immediately with the most important development
   - Mention specific companies, products, or technologies
   - Explain why this matters NOW
   - Be concrete, not generic
   - NO phrases like "Recent developments indicate" or "In today's world"

2. ANALYSIS (180+ words):
   - Provide deep technical and strategic analysis
   - Compare and contrast different sources
   - Identify technical patterns and strategic decisions
   - Discuss implementation details and architecture
   - Include specific examples and data points
   - Show technical expertise

3. IMPLICATIONS (150+ words):
   - Analyze WHO is affected: companies, users, developers, competitors
   - Explain HOW they're affected: market dynamics, product strategies
   - Be concrete and actionable
   - Include specific business implications
   - Mention specific stakeholders by name

4. KEY TAKEAWAYS (120+ words):
   - Synthesize 3-4 key insights readers should remember
   - Each insight must be unique and non-overlapping
   - Strategic clarity and actionable understanding
   - Avoid generic business speak
   - Write as flowing paragraphs, NOT bullet points

5. CONCLUSION (100+ words):
   - Write a forward-looking conclusion
   - Future outlook and strategic direction
   - What this signals about industry evolution
   - Final insight that ties everything together
   - Strong, memorable closing
   - Do NOT repeat earlier sections

Write professionally, avoid jargon, be specific and concrete.
Label each section clearly so it can be parsed."""

        response_text = self._call_gemini(prompt)
        sections = self._parse_sections(response_text)
        
        return sections

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

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse the generated article into sections.
        Handles various formatting patterns from Gemini.
        """
        sections = {}
        
        # Flexible patterns to match different section formats
        patterns = {
            "introduction": r"(?:1\.?\s*INTRODUCTION|1\.?\s*Introduction)[:\s]+(.*?)(?=2\.?\s*(?:ANALYSIS|Analysis)|$)",
            "analysis": r"(?:2\.?\s*ANALYSIS|2\.?\s*Analysis)[:\s]+(.*?)(?=3\.?\s*(?:IMPLICATIONS|Implications)|$)",
            "implications": r"(?:3\.?\s*IMPLICATIONS|3\.?\s*Implications)[:\s]+(.*?)(?=4\.?\s*(?:KEY TAKEAWAYS?|Key Takeaways?)|$)",
            "key_takeaways": r"(?:4\.?\s*KEY TAKEAWAYS?|4\.?\s*Key Takeaways?)[:\s]+(.*?)(?=5\.?\s*(?:CONCLUSION|Conclusion)|$)",
            "conclusion": r"(?:5\.?\s*CONCLUSION|5\.?\s*Conclusion)[:\s]+(.*?)$"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Clean up any extra whitespace
                content = re.sub(r'\n\s*\n', '\n\n', content)
                sections[section] = content
            else:
                # Fallback: empty section if not found
                sections[section] = f"[Section {section} not generated properly]"
                print(f"  Warning: Could not parse {section} section")
        
        return sections

    def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call Google Gemini API with exponential backoff for rate limiting.
        Handles 429 errors specifically.
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
                "maxOutputTokens": 2048,  # Increased for full article generation
            }
        }

        base_wait = 15  # Base wait time in seconds
        
        for attempt in range(max_retries):
            try:
                # Wait before each request to respect rate limits
                if attempt == 0:
                    # First attempt: small delay to avoid bursts
                    time.sleep(5)
                else:
                    # Exponential backoff for retries
                    wait_time = base_wait * (2 ** (attempt - 1))  # 15, 30, 60 seconds
                    print(f"  Retry {attempt}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                response = requests.post(url, json=payload, timeout=90)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract text from Gemini response
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        content = candidate["content"]["parts"][0]["text"]
                        content = content.strip()
                        return content
                    else:
                        raise RuntimeError("Invalid response structure from Gemini")
                else:
                    raise RuntimeError("No content in Gemini response")

            except requests.exceptions.HTTPError as e:
                # Special handling for rate limit errors (429)
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Longer wait for rate limits
                        wait_time = 60 * (2 ** attempt)  # 60, 120, 240 seconds
                        print(f"  Rate limit hit (429). Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Rate limit exceeded after {max_retries} attempts. Try again later.")
                
                # Handle other HTTP errors
                elif e.response.status_code == 404:
                    raise RuntimeError(f"Model not found (404). Check model name: {self.endpoint}")
                
                else:
                    # Other HTTP errors
                    if attempt < max_retries - 1:
                        print(f"  HTTP Error {e.response.status_code}: {e}, retrying...")
                        time.sleep(10)
                        continue
                    else:
                        raise RuntimeError(f"Gemini API HTTP error: {e}")
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"  Request timeout, retrying...")
                    time.sleep(10)
                    continue
                else:
                    raise RuntimeError(f"Gemini API timeout after {max_retries} attempts")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Error: {e}, retrying...")
                    time.sleep(10)
                    continue
                else:
                    raise RuntimeError(f"Gemini API failed after {max_retries} attempts: {e}")

        return ""


def build_article(items: List[Dict]) -> Dict[str, str]:
    """
    Build a complete, high-quality article from news sources.
    Uses single API call for efficiency.
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

    # Generate entire article in ONE API call (much more efficient!)
    print("Generating full article (this may take 30-60 seconds)...")
    sections = generator.generate_full_article(items, angle)
    
    # Verify all sections were generated
    required_sections = ["introduction", "analysis", "implications", "key_takeaways", "conclusion"]
    missing_sections = [s for s in required_sections if s not in sections or not sections[s]]
    
    if missing_sections:
        print(f"  Warning: Missing sections: {missing_sections}")

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
        print(f"  Warning: Article has violations: {violations}")

    # Create meta description
    intro_text = sections.get("introduction", "")
    if len(intro_text) > 160:
        meta_desc = intro_text[:160].rsplit(" ", 1)[0] + "..."
    else:
        meta_desc = intro_text

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
