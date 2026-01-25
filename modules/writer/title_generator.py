# modules/writer/title_generator.py

import random
from typing import List, Dict


TITLE_PATTERNS = {
    "strategic_shift": [
        "What {topic} Signals About the Strategic Direction of the Tech Industry",
        "{topic}: A Strategic Turning Point for Technology Leaders",
        "Why {topic} Marks a Strategic Shift in the Tech Sector",
    ],
    "market_signal": [
        "{topic} and What It Reveals About the Tech Market Right Now",
        "Why {topic} Is Being Read as a Market Signal",
        "{topic}: Investors Are Paying Attention for a Reason",
    ],
    "user_impact": [
        "How {topic} Could Affect Users Sooner Than Expected",
        "What {topic} Means for Everyday Technology Users",
        "{topic} and Its Real Impact on Users",
    ],
    "industry_trend": [
        "{topic} and the Direction the Tech Industry Is Taking",
        "Why {topic} Fits Into a Larger Industry Trend",
        "{topic}: Another Sign of Where Tech Is Headed",
    ],
    "long_term_implication": [
        "The Long-Term Implications of {topic} for the Tech Industry",
        "Why {topic} Could Shape Technology for Years to Come",
        "{topic} and Its Long-Term Impact on Tech Strategy",
    ],
}


def generate_alternative_title(
    original_title: str,
    angle: str,
    items: List[Dict],
) -> str:
    """
    Generate a non-duplicative, editorial-style alternative title.
    """

    topic = original_title.strip()

    patterns = TITLE_PATTERNS.get(angle, TITLE_PATTERNS["industry_trend"])
    pattern = random.choice(patterns)

    return pattern.format(topic=topic)
