# modules/fetcher/rss_fetch.py

import feedparser
import yaml
from pathlib import Path
from typing import List, Dict


SOURCES_PATH = Path("config/sources.yaml")


def _load_sources() -> Dict:
    if not SOURCES_PATH.exists():
        raise FileNotFoundError("sources.yaml not found in config/")

    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("sources", {})


def fetch_all() -> List[Dict]:
    """
    Fetch RSS items from configured sources and attach authority metadata.
    """

    sources = _load_sources()
    all_items: List[Dict] = []

    for source_id, meta in sources.items():
        url = meta["url"]
        authority = float(meta.get("authority", 0.5))
        category = meta.get("category", "unknown")

        feed = feedparser.parse(url)

        for entry in feed.entries:
            item = {
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "category": category,
                "source": source_id,
                "source_authority": authority,
            }

            if item["title"] and item["link"]:
                all_items.append(item)

    return all_items
