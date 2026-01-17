import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fetcher.rss_fetch import fetch_all
from fetcher.cleaner import clean_items
from selector.selector import select_news
from writer.article_builder import build_article

raw_items = fetch_all()
clean_items_list = clean_items(raw_items)
selected = select_news(clean_items_list)

article_text = build_article(selected)

print(article_text)
