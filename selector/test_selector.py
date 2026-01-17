import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fetcher.rss_fetch import fetch_all
from fetcher.cleaner import clean_items
from selector import select_news

raw_items = fetch_all()
clean_items_list = clean_items(raw_items)

selected = select_news(clean_items_list)

print("Selected items:", len(selected))

for item in selected[:5]:
    print("-" * 40)
    print(item["title"])
    print(item["source"], "|", item["category"])
