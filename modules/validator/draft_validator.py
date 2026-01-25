# modules/validator/draft_validator.py

from enum import Enum
from pathlib import Path
import json


class DraftDecision(str, Enum):
    PUBLISH = "PUBLISH"
    HOLD = "HOLD"


HISTORY_PATH = Path("data/validator/history.json")
HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)


class DraftValidator:
    """
    Lightweight validator to prevent duplicate titles
    and enforce basic editorial diversity.
    """

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history = self._load_history()

    def _load_history(self) -> list[str]:
        if not HISTORY_PATH.exists():
            return []

        try:
            data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_history(self) -> None:
        trimmed = self.history[-self.max_history :]
        HISTORY_PATH.write_text(
            json.dumps(trimmed, indent=2),
            encoding="utf-8",
        )

    def decide(self, article: dict) -> dict:
        title = article["title"]

        reasons: list[str] = []

        if title in self.history:
            reasons.append("Duplicate title detected in recent history")

        if reasons:
            return {
                "decision": DraftDecision.HOLD,
                "reasons": reasons,
            }

        # Accept article
        self.history.append(title)
        self._save_history()

        return {
            "decision": DraftDecision.PUBLISH,
            "reasons": [],
        }
