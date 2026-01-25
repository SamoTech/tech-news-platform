# modules/selector/selector.py

import random
from collections import defaultdict
from typing import List, Dict


TARGET_TOTAL = 45
CATEGORY_QUOTA = 5


def _score_item(item: Dict) -> float:
    """
    Calculate a weighted editorial score for each news item.
    """

    base = 1.0

    authority = float(item.get("source_authority", 0.5))
    base *= authority * 2  # authority is dominant factor

    title = item.get("title", "").lower()

    # Boost for analysis-worthy keywords
    if any(k in title for k in ["regulation", "policy", "security", "ai", "privacy"]):
        base += 0.6

    if any(k in title for k in ["raises", "funding", "acquires", "ipo"]):
        base += 0.4

    # Penalize fluff / low-signal
    if any(k in title for k in ["review", "hands-on", "leak", "rumor"]):
        base -= 0.5

    return max(base, 0.1)


def select_news(items: List[Dict]) -> List[Dict]:
    """
    Select a balanced, authority-weighted set of news items.
    """

    if not items:
        return []

    # Attach score
    for item in items:
        item["weight"] = _score_item(item)

    # Group by category
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get("category", "unknown")].append(item)

    selected: List[Dict] = []

    # Category-first selection
    for category, bucket in grouped.items():
        if not bucket:
            continue

        bucket = sorted(bucket, key=lambda x: x["weight"], reverse=True)

        take = min(CATEGORY_QUOTA, len(bucket))
        selected.extend(bucket[:take])

    # Fill remaining slots globally
    if len(selected) < TARGET_TOTAL:
        remaining = [i for i in items if i not in selected]
        remaining = sorted(remaining, key=lambda x: x["weight"], reverse=True)

        needed = TARGET_TOTAL - len(selected)
        selected.extend(remaining[:needed])

    # Final shuffle (light)
    random.shuffle(selected)

    return selected
