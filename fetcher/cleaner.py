import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_text(text):
    soup = BeautifulSoup(text, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def deduplicate(items):
    seen = set()
    clean_items = []

    for item in items:
        key = (item["title"].lower(), normalize_url(item["link"]))
        if key in seen:
            continue
        seen.add(key)
        clean_items.append(item)

    return clean_items

def clean_items(items):
    cleaned = []

    for item in items:
        if len(item["title"]) < 20:
            continue

        item["summary"] = clean_text(item["summary"])
        item["link"] = normalize_url(item["link"])

        cleaned.append(item)

    return deduplicate(cleaned)
