# run_pipeline.py

from pathlib import Path
from datetime import datetime, UTC

from modules.fetcher.rss_fetch import fetch_all
from modules.selector.selector import select_news
from modules.writer.article_builder import build_article
from modules.writer.rewriter import ArticleRewriter
from modules.validator.draft_validator import DraftValidator, DraftDecision
from modules.publisher.blogger_publisher import BloggerPublisher


# =========================
# CONFIG
# =========================
BLOG_ID = "7570751768424346777"  # Blogger Blog ID
DRY_RUN = False                # True = build only, False = publish
MAX_ATTEMPTS = 5
MIN_WORDS_AFTER_REWRITE = 700

DATA_DIR = Path("data/drafts")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace(",", "")
        .replace("’", "")
        .replace("'", "")
    )


def main():
    publisher = BloggerPublisher(BLOG_ID)
    validator = DraftValidator()
    rewriter = ArticleRewriter()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nATTEMPT {attempt}/{MAX_ATTEMPTS}")

        # 1. Fetch & select news
        items = fetch_all()
        selected = select_news(items)

        # 2. Build base article (700+ words guaranteed)
        article = build_article(selected[:3])

        # 3. Rewrite article SECTIONS (safe rewrite)
        article["content"] = rewriter.rewrite_article_sections(
            article["content"],
            min_words=MIN_WORDS_AFTER_REWRITE,
        )

        # 4. Validate final article
        decision = validator.decide(article)
        print(f"DECISION: {decision['decision']}")

        if decision.get("reasons"):
            for r in decision["reasons"]:
                print(f"- {r}")

        if decision["decision"] != DraftDecision.PUBLISH:
            continue

        # 5. Save local draft
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        filename = f"{date_str}-{slugify(article['title'])}.html"
        output_path = DATA_DIR / filename
        output_path.write_text(article["content"], encoding="utf-8")

        # 6. Publish
        if DRY_RUN:
            print("DRY RUN — NOT PUBLISHED")
        else:
            result = publisher.publish(article)
            print("PUBLISHED TO BLOGGER")
            print("URL:", result.get("url"))

        # 7. Final log
        print("Saved:", output_path)
        print("Title:", article["title"])
        print("Angle:", article.get("angle"))
        print("Word count:", len(article["content"].split()))
        print("Meta:", article["meta_description"][:120])

        return

    print("\nFAILED: No publishable article after max attempts")


if __name__ == "__main__":
    main()
