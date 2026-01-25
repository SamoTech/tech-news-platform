# modules/writer/authors.py

from typing import Dict, List
import random


CORE_AUTHORS: Dict[str, Dict] = {
    "alex_morgan": {
        "name": "Alex Morgan",
        "role": "AI & Policy Analyst",
        "topics": ["ai", "policy", "regulation", "government"],
    },
    "sarah_klein": {
        "name": "Sarah Klein",
        "role": "Digital Infrastructure Researcher",
        "topics": ["cloud", "infrastructure", "data", "systems"],
    },
    "michael_chen": {
        "name": "Michael Chen",
        "role": "Enterprise Technology Editor",
        "topics": ["enterprise", "business", "security", "platform"],
    },
}


EXTENDED_AUTHORS: Dict[str, Dict] = {
    "emily_rodriguez": {
        "name": "Emily Rodriguez",
        "role": "Health Tech Analyst",
        "topics": ["health", "biotech", "medical"],
    },
    "daniel_park": {
        "name": "Daniel Park",
        "role": "Consumer AI Researcher",
        "topics": ["consumer", "apps", "ui", "assistant"],
    },
}


def select_author(
    title: str,
    angle: str,
    used_authors: List[str],
    allow_extended: bool = False,
) -> Dict[str, str]:
    """
    Deterministic-first author selection with controlled randomness.
    """

    title_lower = title.lower()

    # 1. Try core authors first
    for author in CORE_AUTHORS.values():
        if any(t in title_lower for t in author["topics"]):
            return author

    # 2. Extended authors only if explicitly allowed
    if allow_extended:
        for author in EXTENDED_AUTHORS.values():
            if (
                any(t in title_lower for t in author["topics"])
                and author["name"] not in used_authors
            ):
                return author

    # 3. Fallback: least recently used core author
    for author in CORE_AUTHORS.values():
        if author["name"] not in used_authors:
            return author

    # 4. Absolute fallback
    return random.choice(list(CORE_AUTHORS.values()))
