import feedparser
import yaml
from datetime import datetime, timedelta

MAX_AGE_HOURS = 48

def load_sources(path="config/sources.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def is_fresh(entry):
    published = getattr(entry, "published_parsed", None)
    if not published:
        return False
    published_dt = datetime(*published[:6])
    return datetime.utcnow() - published_dt <= timedelta(hours=MAX_AGE_HOURS)

def fetch_feed(source_name, rss_url, category, weight):
    feed = feedparser.parse(rss_url)
    items = []

    for entry in feed.entries:
        if not is_fresh(entry):
            continue

        items.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", "").strip(),
            "summary": entry.get("summary", "").strip(),
            "category": category,
            "source": source_name,
            "weight": weight
        })

    return items

def fetch_all():
    sources = load_sources()
    all_items = []

    for category, feeds in sources.items():
        for feed in feeds:
            items = fetch_feed(
                feed["name"],
                feed["rss"],
                category,
                feed["weight"]
            )
            all_items.extend(items)

    return all_items
