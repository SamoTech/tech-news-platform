# run_pipeline.py

from pathlib import Path
from datetime import datetime, UTC

from modules.fetcher.rss_fetch import fetch_all
from modules.selector.selector import select_news
from modules.writer.article_builder import build_article
from modules.validator.draft_validator import DraftValidator, DraftDecision


# =========================
# CONFIG
# =========================
DRY_RUN = True
MAX_ATTEMPTS = 5  # editorial retries

DATA_DIR = Path("data/drafts")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace(",", "")
        .replace("â€™", "")
    )


def main():
    items = fetch_all()
    selected = select_news(items)

    validator = DraftValidator()

    for attempt in range(MAX_ATTEMPTS):
        print(f"\nATTEMPT {attempt + 1}/{MAX_ATTEMPTS}")

        slice_start = attempt * 3
        slice_end = slice_start + 3
        batch = selected[slice_start:slice_end]

        if not batch:
            print("No more news batches available.")
            return

        article = build_article(batch)
        decision = validator.decide(article)

        print(f"DECISION: {decision['decision']}")
        for r in decision["reasons"]:
            print(f"- {r}")

        if decision["decision"] != DraftDecision.PUBLISH:
            continue

        # SUCCESS
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        filename = f"{date_str}-{slugify(article['title'])}.html"
        output_path = DATA_DIR / filename

        output_path.write_text(article["content"], encoding="utf-8")

        print("\nPUBLISHED")
        print("Saved:", output_path)
        print("Title:", article["title"])
        print("Word count:", len(article["content"].split()))
        print("Meta:", article["meta_description"][:120])
        return

    print("\nEDITORIAL HOLD: no suitable article found today.")


if __name__ == "__main__":
    main()
