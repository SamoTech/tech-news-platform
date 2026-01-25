from modules.writer.rules_engine import ArticleRules

rules = ArticleRules()

sample_text = "Short article without structure."

violations = rules.validate_article(sample_text)

print("Violations found:")
for v in violations:
    print("-", v)
