# modules/writer/memory.py

from typing import List
from collections import Counter
from datetime import datetime, timedelta


class ArticleMemory:
    """
    Persistent-like short-term editorial memory.
    """

    def __init__(self, max_items: int = 30, window_hours: int = 72):
        self.max_items = max_items
        self.window = timedelta(hours=window_hours)

        self.recent_titles: List[str] = []
        self.recent_angles: List[str] = []
        self.timestamps: List[datetime] = []

    def _trim(self):
        if len(self.recent_titles) > self.max_items:
            self.recent_titles = self.recent_titles[-self.max_items :]
            self.recent_angles = self.recent_angles[-self.max_items :]
            self.timestamps = self.timestamps[-self.max_items :]

    def remember_titles(self, titles: List[str]) -> None:
        now = datetime.utcnow()
        for t in titles:
            if t and t not in self.recent_titles:
                self.recent_titles.append(t)
                self.timestamps.append(now)
        self._trim()

    def remember_angle(self, angle: str) -> None:
        self.recent_angles.append(angle)
        self._trim()

    def has_seen(self, title: str) -> bool:
        return title in self.recent_titles

    def angle_ratio(self, angle: str) -> float:
        if not self.recent_angles:
            return 0.0
        counts = Counter(self.recent_angles)
        return counts.get(angle, 0) / len(self.recent_angles)
