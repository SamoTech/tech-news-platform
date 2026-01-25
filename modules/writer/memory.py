# modules/writer/memory.py

import json
from pathlib import Path
from datetime import datetime, UTC
from typing import List


MEMORY_PATH = Path("data/memory.json")
MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)


class ArticleMemory:
    """
    Persistent editorial memory with backward-safe schema.
    """

    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self.data = self._load_and_upgrade()

    def _load_and_upgrade(self) -> dict:
        if MEMORY_PATH.exists():
            data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        else:
            data = {}

        # ---- Schema upgrade (backward compatible) ----
        data.setdefault("titles", [])
        data.setdefault("angles", [])
        data.setdefault("authors", [])
        data.setdefault("last_updated", None)

        return data

    def _save(self) -> None:
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        MEMORY_PATH.write_text(
            json.dumps(self.data, indent=2),
            encoding="utf-8",
        )

    def _append(self, key: str, value: str) -> None:
        if value and value not in self.data[key]:
            self.data[key].append(value)

        # Trim history
        self.data[key] = self.data[key][-self.max_items :]

    # -------- Public API --------

    def remember(self, *, title: str, angle: str, author: str) -> None:
        self._append("titles", title)
        self._append("angles", angle)
        self._append("authors", author)
        self._save()

    def has_seen_title(self, title: str) -> bool:
        return title in self.data["titles"]

    def angle_usage_ratio(self, angle: str) -> float:
        if not self.data["angles"]:
            return 0.0
        return self.data["angles"].count(angle) / len(self.data["angles"])

    def recent_authors(self) -> List[str]:
        return list(self.data["authors"])
