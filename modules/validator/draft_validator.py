# modules/validator/draft_validator.py

from enum import Enum
from typing import Dict, List
from datetime import datetime, timedelta

from modules.writer.memory import ArticleMemory


class DraftDecision(str, Enum):
    PUBLISH = "PUBLISH"
    HOLD = "HOLD"


class DraftValidator:
    """
    Editorial validator that simulates a human editor decision.
    """

    def __init__(
        self,
        min_word_count: int = 700,
        min_authority: float = 0.75,
        max_angle_ratio: float = 0.6,
        history_window_hours: int = 48,
    ):
        self.min_word_count = min_word_count
        self.min_authority = min_authority
        self.max_angle_ratio = max_angle_ratio
        self.history_window = timedelta(hours=history_window_hours)

        self.memory = ArticleMemory()

    def _average_authority(self, article: Dict) -> float:
        sources = article.get("sources", [])
        if not sources:
            return 0.0
        return sum(sources) / len(sources)

    def _word_count(self, content: str) -> int:
        return len(content.split())

    def decide(self, article: Dict) -> Dict:
        """
        Return editorial decision and reasons.
        """

        reasons: List[str] = []

        title = article.get("title", "")
        content = article.get("content", "")
        angle = article.get("angle", "unknown")

        # 1. Duplicate title check
        if self.memory.has_seen(title):
            reasons.append("Duplicate title detected in recent history")

        # 2. Word count enforcement
        wc = self._word_count(content)
        if wc < self.min_word_count:
            reasons.append(
                f"Word count below threshold ({wc} < {self.min_word_count})"
            )

        # 3. Angle saturation control
        angle_ratio = self.memory.angle_ratio(angle)
        if angle_ratio > self.max_angle_ratio:
            reasons.append(
                f"Angle overused recently ({angle}, ratio={angle_ratio:.2f})"
            )

        # 4. Authority gate (optional, future-ready)
        avg_authority = self._average_authority(article)
        if avg_authority and avg_authority < self.min_authority:
            reasons.append(
                f"Average source authority too low ({avg_authority:.2f})"
            )

        # Decision
        if reasons:
            return {
                "decision": DraftDecision.HOLD,
                "reasons": reasons,
            }

        # Remember successful publication context
        self.memory.remember_titles([title])
        self.memory.remember_angle(angle)

        return {
            "decision": DraftDecision.PUBLISH,
            "reasons": [],
        }
