from fetcher.rss_fetch import fetch_all
from fetcher.cleaner import clean_items
from selector.selector import select_news
from selector.trending import extract_trends
from writer.article_builder import build_article
from writer.post_formatter import build_post
from publisher.blogger import publish_post

def main():
    raw_items = fetch_all()
    clean_items_list = clean_items(raw_items)
    selected = select_news(clean_items_list)
    trends = extract_trends(selected)

    article_text = build_article(selected)
    post = build_post(article_text, trends)

    publish_post(
        title=post["title"],
        content=post["content"]
    )

if __name__ == "__main__":
    main()
