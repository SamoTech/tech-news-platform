# modules/validator/draft_validator.py

import re
import hashlib
from enum import Enum
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Dict
import json


class DraftDecision(str, Enum):
    PUBLISH = "PUBLISH"
    HOLD = "HOLD"


HISTORY_PATH = Path("data/validator/history.json")
HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)


class DraftValidator:
    """
    Comprehensive validator for content quality, uniqueness, and editorial standards.
    """

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load validation history with proper structure."""
        if not HISTORY_PATH.exists():
            return []

        try:
            data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            # Handle old format
            return []
        except Exception:
            return []

    def _save_history(self) -> None:
        """Save validation history."""
        trimmed = self.history[-self.max_history:]
        HISTORY_PATH.write_text(
            json.dumps(trimmed, indent=2),
            encoding="utf-8",
        )

    def decide(self, article: dict) -> dict:
        """
        Comprehensive validation decision.
        """
        title = article.get("title", "")
        content = article.get("content", "")
        angle = article.get("angle", "unknown")

        reasons: List[str] = []

        # Check 1: Duplicate title
        if self._is_duplicate_title(title):
            reasons.append("Duplicate title detected in recent history")

        # Check 2: Content repetition detection
        repetition_score = self._detect_repetition(content)
        if repetition_score > 0.3:  # More than 30% repetitive
            reasons.append(
                f"High content repetition detected: {repetition_score:.1%}"
            )

        # Check 3: Generic content detection
        if self._is_generic_content(content):
            reasons.append("Content appears too generic or template-like")

        # Check 4: Minimum quality threshold
        quality_score = self._calculate_quality_score(content)
        if quality_score < 0.6:  # Below 60%
            reasons.append(
                f"Content quality below threshold: {quality_score:.1%}"
            )

        # Check 5: Angle diversity (don't overuse same angle)
        if self._angle_overused(angle):
            reasons.append(f"Angle '{angle}' has been overused recently")

        # Check 6: Word count
        word_count = len(content.split())
        if word_count < 700:
            reasons.append(f"Word count too low: {word_count} words")

        # Decide
        if reasons:
            return {
                "decision": DraftDecision.HOLD,
                "reasons": reasons,
                "quality_score": quality_score,
            }

        # Accept and record
        self._record_article(title, content, angle)

        return {
            "decision": DraftDecision.PUBLISH,
            "reasons": [],
            "quality_score": quality_score,
        }

    def _is_duplicate_title(self, title: str) -> bool:
        """Check if title exists in history."""
        title_lower = title.lower().strip()
        for entry in self.history:
            if entry.get("title", "").lower().strip() == title_lower:
                return True
        return False

    def _detect_repetition(self, content: str) -> float:
        """
        Detect repetitive content by checking for repeated sentences/phrases.
        Returns repetition ratio (0.0 = no repetition, 1.0 = all repetitive)
        """
        # Extract sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if len(sentences) < 3:
            return 0.0

        # Count duplicates
        seen = {}
        duplicates = 0

        for sentence in sentences:
            # Normalize
            normalized = re.sub(r'\s+', ' ', sentence.lower())
            
            if normalized in seen:
                duplicates += 1
            else:
                seen[normalized] = 1

        return duplicates / len(sentences)

    def _is_generic_content(self, content: str) -> bool:
        """
        Detect generic, template-like content.
        """
        content_lower = content.lower()

        # Red flag phrases (generic AI-generated content)
        generic_phrases = [
            "from a strategic standpoint",
            "organizations are increasingly prioritizing",
            "driven by regulatory and operational pressures",
            "in today's rapidly evolving",
            "as we move forward",
            "it is important to note that",
            "in conclusion, it can be said",
            "this article discusses",
        ]

        phrase_count = sum(1 for phrase in generic_phrases if phrase in content_lower)

        # If 3+ generic phrases found, likely template content
        return phrase_count >= 3

    def _calculate_quality_score(self, content: str) -> float:
        """
        Calculate overall content quality score (0.0 - 1.0).
        """
        score = 1.0

        # Penalty for repetition
        repetition = self._detect_repetition(content)
        score -= repetition * 0.4

        # Penalty for generic content
        if self._is_generic_content(content):
            score -= 0.3

        # Penalty for lack of specificity (too many generic words)
        words = content.lower().split()
        generic_words = ["various", "multiple", "several", "numerous", "many", "some"]
        generic_ratio = sum(1 for w in words if w in generic_words) / max(len(words), 1)
        score -= generic_ratio * 0.2

        # Bonus for specific technical terms
        technical_terms = ["api", "algorithm", "infrastructure", "implementation", 
                          "architecture", "protocol", "framework", "deployment"]
        tech_ratio = sum(1 for w in words if w in technical_terms) / max(len(words), 1)
        score += min(tech_ratio * 100, 0.1)  # Small bonus

        return max(min(score, 1.0), 0.0)

    def _angle_overused(self, angle: str) -> bool:
        """
        Check if an angle has been used too frequently recently.
        """
        if len(self.history) < 5:
            return False

        recent = self.history[-10:]
        angle_count = sum(1 for entry in recent if entry.get("angle") == angle)

        # More than 40% of recent articles
        return angle_count > len(recent) * 0.4

    def _record_article(self, title: str, content: str, angle: str) -> None:
        """
        Record article in history.
        """
        # Create content hash for future similarity detection
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        title_hash = hashlib.sha256(title.encode()).hexdigest()

        entry = {
            "date": datetime.now(UTC).isoformat(),
            "title": title,
            "title_hash": title_hash,
            "content_hash": content_hash,
            "angle": angle,
            "word_count": len(content.split()),
        }

        self.history.append(entry)
        self._save_history()

    def get_stats(self) -> Dict:
        """
        Get validation statistics.
        """
        if not self.history:
            return {"total": 0}

        angles = {}
        for entry in self.history:
            angle = entry.get("angle", "unknown")
            angles[angle] = angles.get(angle, 0) + 1

        return {
            "total": len(self.history),
            "angles": angles,
            "recent_titles": [e.get("title") for e in self.history[-5:]],
        }
