# run_pipeline.py

import os
import json
from pathlib import Path
from datetime import datetime, UTC

from modules.fetcher.rss_fetch import fetch_all
from modules.fetcher.cleaner import clean_items
from modules.selector.selector import select_news
from modules.writer.article_builder import build_article
from modules.writer.internal_links import inject_internal_links
from modules.validator.draft_validator import DraftValidator, DraftDecision
from modules.publisher.blogger_publisher import BloggerPublisher


# =========================
# CONFIG
# =========================
BLOG_ID = os.getenv("BLOGGER_BLOG_ID", "7570751768424346777")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
MAX_ATTEMPTS = 5

DATA_DIR = Path("data/drafts")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    """Convert title to URL-friendly slug."""
    return (
        text.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace(",", "")
        .replace("'", "")
        .replace("'", "")
        .replace(":", "")
        .replace("?", "")
        .replace("!", "")
        [:100]  # Limit length
    )


def save_draft(article: dict, metadata: dict) -> Path:
    """
    Save article draft and metadata to disk.
    """
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    slug = slugify(article['title'])
    
    # Save HTML
    html_path = DATA_DIR / f"{date_str}-{slug}.html"
    html_path.write_text(article["content"], encoding="utf-8")
    
    # Save metadata
    json_path = DATA_DIR / f"{date_str}-{slug}.json"
    json_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8"
    )
    
    return html_path


def main():
    """
    Main pipeline execution with improved error handling and logging.
    """
    print("=" * 60)
    print("TECH NEWS PUBLISHING PIPELINE")
    print("=" * 60)
    print(f"Dry Run: {DRY_RUN}")
    print(f"Max Attempts: {MAX_ATTEMPTS}")
    print()

    # Initialize components
    try:
        validator = DraftValidator()
        print("✓ Validator initialized")
        
        if not DRY_RUN:
            publisher = BloggerPublisher(BLOG_ID)
            print("✓ Publisher initialized")
        else:
            publisher = None
            print("✓ Dry run mode (no publishing)")
            
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return

    # Display validator stats
    stats = validator.get_stats()
    print(f"\nValidator Stats:")
    print(f"  Total articles validated: {stats.get('total', 0)}")
    if stats.get('angles'):
        print(f"  Angle distribution: {stats['angles']}")
    print()

    # Main attempt loop
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n{'=' * 60}")
        print(f"ATTEMPT {attempt}/{MAX_ATTEMPTS}")
        print(f"{'=' * 60}\n")

        try:
            # Step 1: Fetch news
            print("Step 1: Fetching RSS feeds...")
            raw_items = fetch_all()
            print(f"  Fetched {len(raw_items)} raw items")

            if not raw_items:
                print("  ✗ No items fetched")
                continue

            # Step 2: Clean items
            print("\nStep 2: Cleaning items...")
            items = clean_items(raw_items)
            print(f"  Cleaned to {len(items)} items")

            if not items:
                print("  ✗ No items after cleaning")
                continue

            # Step 3: Select best news
            print("\nStep 3: Selecting news items...")
            selected = select_news(items)
            print(f"  Selected {len(selected)} items for synthesis")

            if len(selected) < 3:
                print("  ✗ Not enough items selected")
                continue

            # Display selected items
            print("\n  Top 3 sources:")
            for i, item in enumerate(selected[:3], 1):
                print(f"    {i}. {item.get('title', 'N/A')[:70]}...")
                print(f"       Source: {item.get('source')} | Authority: {item.get('source_authority')}")

            # Step 4: Build article
            print("\nStep 4: Generating article content...")
            print("  (This may take 30-60 seconds...)")
            article = build_article(selected[:3])
            
            print(f"  ✓ Article generated")
            print(f"    Title: {article['title']}")
            print(f"    Angle: {article['angle']}")
            print(f"    Word count: {article['word_count']}")

            # Step 5: Add internal links
            print("\nStep 5: Adding internal links...")
            article["content"] = inject_internal_links(article["content"])
            print("  ✓ Internal links added")

            # Step 6: Validate
            print("\nStep 6: Validating article...")
            decision = validator.decide(article)
            
            print(f"  Decision: {decision['decision']}")
            print(f"  Quality Score: {decision.get('quality_score', 0):.1%}")
            
            if decision.get("reasons"):
                print("  Rejection reasons:")
                for reason in decision["reasons"]:
                    print(f"    - {reason}")

            if decision["decision"] != DraftDecision.PUBLISH:
                print("\n  ✗ Article rejected, trying again...")
                continue

            # Step 7: Save draft
            print("\nStep 7: Saving draft...")
            metadata = {
                "title": article["title"],
                "slug": slugify(article["title"]),
                "publish_date": datetime.now(UTC).isoformat(),
                "word_count": article["word_count"],
                "primary_angle": article["angle"],
                "source_titles": article.get("source_titles", []),
                "quality_score": decision.get("quality_score", 0),
                "status": "published" if not DRY_RUN else "draft",
            }
            
            draft_path = save_draft(article, metadata)
            print(f"  ✓ Draft saved: {draft_path}")

            # Step 8: Publish
            if DRY_RUN:
                print("\n✓ DRY RUN COMPLETE - Article not published")
                print(f"\nDraft location: {draft_path}")
            else:
                print("\nStep 8: Publishing to Blogger...")
                try:
                    result = publisher.publish(article)
                    print(f"  ✓ Published successfully")
                    print(f"    Post ID: {result.get('post_id')}")
                    print(f"    URL: {result.get('url')}")
                    
                    # Update metadata with published URL
                    metadata["status"] = "published"
                    metadata["published_url"] = result.get("url")
                    metadata["post_id"] = result.get("post_id")
                    
                    # Re-save metadata
                    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
                    slug = slugify(article['title'])
                    json_path = DATA_DIR / f"{date_str}-{slug}.json"
                    json_path.write_text(
                        json.dumps(metadata, indent=2),
                        encoding="utf-8"
                    )
                    
                except Exception as e:
                    print(f"  ✗ Publishing failed: {e}")
                    print("  Article saved as draft only")

            # Success!
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"\nTitle: {article['title']}")
            print(f"Angle: {article['angle']}")
            print(f"Word count: {article['word_count']}")
            print(f"Quality score: {decision.get('quality_score', 0):.1%}")
            print(f"\nMeta description:")
            print(f"  {article['meta_description']}")
            
            return

        except Exception as e:
            print(f"\n✗ Error in attempt {attempt}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # All attempts failed
    print("\n" + "=" * 60)
    print("PIPELINE FAILED")
    print("=" * 60)
    print(f"\nNo publishable article generated after {MAX_ATTEMPTS} attempts.")
    print("\nPossible issues:")
    print("  - News sources unavailable")
    print("  - API rate limits")
    print("  - Content quality too low")
    print("  - All titles already used")
    print("\nCheck logs above for specific errors.")


if __name__ == "__main__":
    main()
