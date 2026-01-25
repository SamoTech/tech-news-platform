# modules/validator/draft_validator.py

from enum import Enum
from pathlib import Path
import json

from modules.writer.memory import ArticleMemory


class DraftDecision(str, Enum):
    PUBLISH = "PUBLISH"
    HOLD = "HOLD"


class DraftValidator:
    """
    Editorial gatekeeper with graceful fallback.
    """

    def __init__(self, history_path: str = "data/validator/history.json"):
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        if self.history_path.exists():
            self.history = json.loads(self.history_path.read_text(encoding="utf-8"))
        else:
            self.history = {"titles": [], "angles": []}

        self.memory = ArticleMemory()

    def decide(self, article: dict) -> dict:
        reasons = []

        title = article.get("title", "")
        angle = article.get("angle", "unknown")

        if title in self.history["titles"]:
            reasons.append("Duplicate title detected in recent history")

        if angle in self.history["angles"]:
            reasons.append("Angle overused recently")

        # HARD BLOCK only if BOTH repeat
        if len(reasons) >= 2:
            decision = DraftDecision.HOLD
        else:
            decision = DraftDecision.PUBLISH

        if decision == DraftDecision.PUBLISH:
            self._commit(article)

        return {
            "decision": decision,
            "reasons": reasons,
        }

    def _commit(self, article: dict):
        self.history["titles"].append(article["title"])
        self.history["angles"].append(article.get("angle", "unknown"))

        self.history["titles"] = self.history["titles"][-50:]
        self.history["angles"] = self.history["angles"][-50:]

        self.history_path.write_text(
            json.dumps(self.history, indent=2),
            encoding="utf-8",
        )
