# modules/writer/article_builder.py

from datetime import datetime
from typing import List, Dict

from modules.writer.angles import choose_angle
from modules.writer.memory import ArticleMemory
from modules.writer.templates import render_article
from modules.writer.rules_engine import ArticleRules
from modules.writer.authors import select_author


MIN_WORDS = 700


def _expand_paragraph(base: str, angle: str) -> str:
    expansions = {
        "strategic_shift": (
            "From a strategic standpoint, this development reflects a broader realignment "
            "within the technology sector, driven by regulatory, economic, and operational pressure."
        ),
        "market_signal": (
            "Viewed as a market signal, this move highlights changing investor expectations "
            "and competitive dynamics across the industry."
        ),
        "user_impact": (
            "For end users, the impact is tangible. Platform-level changes often surface "
            "later as shifts in usability, pricing, or reliability."
        ),
        "industry_trend": (
            "At the industry level, this aligns with a longer-term trend toward consolidation "
            "and abstraction of complexity."
        ),
        "long_term_implication": (
            "Over time, decisions like this tend to redefine norms, best practices, "
            "and competitive baselines."
        ),
    }

    return f"{base}\n\n{expansions.get(angle, expansions['industry_trend'])}"


def _ensure_minimum_length(sections: Dict[str, str], angle: str) -> Dict[str, str]:
    def wc(text: str) -> int:
        return len(text.split())

    combined = " ".join(sections.values())

    while wc(combined) < MIN_WORDS:
        for key in sections:
            sections[key] = _expand_paragraph(sections[key], angle)
            combined = " ".join(sections.values())
            if wc(combined) >= MIN_WORDS:
                break

    return sections


def build_article(items: List[Dict]) -> Dict[str, str]:
    if not items:
        raise ValueError("No items provided")

    rules = ArticleRules()
    memory = ArticleMemory()

    titles = [i.get("title", "") for i in items]
    angle = choose_angle(items)

    author = select_author(
        title=titles[0],
        angle=angle,
        used_authors=memory.recent_authors(),
        allow_extended=True,
    )

    sections = {
        "introduction": (
            "Recent developments point to a clear shift in how technology leaders "
            "are approaching innovation and risk."
        ),
        "analysis": (
            "When viewed together, these developments suggest deliberate trade-offs "
            "between speed, control, and long-term sustainability."
        ),
        "implications": (
            "The implications extend beyond individual companies, shaping ecosystems "
            "and influencing downstream product decisions."
        ),
        "key_takeaways": (
            "The key takeaway is not the headline itself, but the direction it signals "
            "for the broader technology landscape."
        ),
        "conclusion": (
            "Overall, this reflects a maturing phase in the sector, where execution "
            "and accountability matter more than novelty."
        ),
    }

    sections = _ensure_minimum_length(sections, angle)

    article_html = render_article(
        title=titles[0],
        sections=sections,
        angle=angle,
        author=f"{author['name']} — {author['role']}",
        date=datetime.utcnow().strftime("%B %d, %Y"),
    )

    violations = rules.validate_article(article_html)
    if violations:
        raise ValueError(f"Article rules violated: {violations}")

    memory.remember(
        title=titles[0],
        angle=angle,
        author=author["name"],
    )

    return {
        "title": titles[0],
        "content": article_html,
        "meta_description": (
            "An in-depth analysis of recent technology developments, examining strategic "
            "implications, market signals, and long-term impact."
        ),
        "angle": angle,
    }
