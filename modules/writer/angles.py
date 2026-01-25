# modules/writer/angles.py

import random
from typing import List, Dict


ANGLES = [
    "strategic_shift",
    "market_signal",
    "user_impact",
    "industry_trend",
    "long_term_implication"
]


def choose_angle(items: List[Dict]) -> str:
    """
    Select an editorial angle based on the nature of the news items.
    This is intentionally deterministic-light to keep articles human-like.
    """

    if not items:
        return "industry_trend"

    titles = " ".join(item.get("title", "").lower() for item in items)

    if any(k in titles for k in ["regulation", "policy", "law", "ban"]):
        return "strategic_shift"

    if any(k in titles for k in ["funding", "raises", "investment", "acquisition"]):
        return "market_signal"

    if any(k in titles for k in ["user", "consumer", "customer", "feature"]):
        return "user_impact"

    if any(k in titles for k in ["2026", "future", "next", "roadmap"]):
        return "long_term_implication"

    return random.choice(ANGLES)
