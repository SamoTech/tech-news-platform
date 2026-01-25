# run_pipeline.py

from pathlib import Path
from datetime import datetime, UTC

from modules.fetcher.rss_fetch import fetch_all
from modules.selector.selector import select_news
from modules.writer.article_builder import build_article
from modules.validator.draft_validator import DraftValidator, DraftDecision
from modules.publisher.blogger_publisher import BloggerPublisher


# =========================
# CONFIG
# =========================
BLOG_ID = "7570751768424346777"
DRY_RUN = False  # True = no publishing, False = publish to Blogger
MAX_ATTEMPTS = 5

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

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nATTEMPT {attempt}/{MAX_ATTEMPTS}")

        items = fetch_all()
        selected = select_news(items)
        article = build_article(selected[:3])

        decision = validator.decide(article)
        print(f"DECISION: {decision['decision']}")

        if decision["reasons"]:
            for r in decision["reasons"]:
                print(f"- {r}")

        if decision["decision"] != DraftDecision.PUBLISH:
            continue

        # Save local draft (always)
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        filename = f"{date_str}-{slugify(article['title'])}.html"
        output_path = DATA_DIR / filename
        output_path.write_text(article["content"], encoding="utf-8")

        if DRY_RUN:
            print("DRY RUN — NOT PUBLISHED")
        else:
            result = publisher.publish(article)
            print("PUBLISHED TO BLOGGER")
            print("Post ID:", result.get("id"))
            print("URL:", result.get("url"))

        print("Saved:", output_path)
        print("Title:", article["title"])
        print("Angle:", article.get("angle"))
        print("Word count:", len(article["content"].split()))
        print("Meta:", article["meta_description"][:120])

        return

    print("\nFAILED: No publishable article after max attempts")


if __name__ == "__main__":
    main()
