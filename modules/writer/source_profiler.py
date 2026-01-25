# modules/writer/source_profiler.py

from collections import Counter
from typing import List, Dict


def build_source_profile(items: List[Dict]) -> Dict[str, float]:
    """
    Build a normalized source authority profile from selected items.
    """

    if not items:
        return {"authoritative": 0.0, "commercial": 0.0, "community": 0.0}

    scores = {"authoritative": 0.0, "commercial": 0.0, "community": 0.0}

    for item in items:
        authority = item.get("source_authority", 0.5)
        source = item.get("source", "")

        if source in {"google", "microsoft", "aws", "mit"}:
            scores["authoritative"] += authority
        elif source in {"techcrunch", "wired"}:
            scores["commercial"] += authority
        else:
            scores["community"] += authority

    total = sum(scores.values()) or 1.0
    return {k: round(v / total, 2) for k, v in scores.items()}
