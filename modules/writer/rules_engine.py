# modules/writer/rules_engine.py

import yaml
from pathlib import Path

RULES_PATH = Path("config/article_rules.yaml")


class ArticleRules:
    def __init__(self, rules_path: Path = RULES_PATH):
        if not rules_path.exists():
            raise FileNotFoundError(f"Rules file not found: {rules_path}")

        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f)

    def get(self):
        return self.rules
    def validate_article(self, article_text: str) -> list:
        """
        Validate article against mandatory rules.
        Returns a list of violations. Empty list = valid.
        """
        violations = []

        rules = self.rules

        # Word count
        min_words = rules["article"]["minimum_word_count"]
        word_count = len(article_text.split())
        if word_count < min_words:
            violations.append(
                f"Word count too low: {word_count} < {min_words}"
            )

        # Forbidden patterns
        forbidden = rules["content_quality"]["forbidden_patterns"]
        for phrase in forbidden:
            if phrase.lower() in article_text.lower():
                violations.append(f"Forbidden phrase detected: '{phrase}'")

        # Required sections
        required_sections = rules["structure"]["required_sections"]
        for section in required_sections:
            if section.replace("_", " ").lower() not in article_text.lower():
                violations.append(f"Missing required section: {section}")

        return violations
