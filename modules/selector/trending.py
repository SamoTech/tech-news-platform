import re
from collections import Counter

STOPWORDS = {
    "this","that","with","from","have","will","about",
    "after","before","their","there","which","when",
    "what","where","while","could","would","should"
}

def tokenize(text):
    return re.findall(r"[A-Za-z]{4,}", text.lower())

def extract_trends(items, top_n=5):
    counter = Counter()

    for item in items:
        words = tokenize(item["title"])
        for word in words:
            if word in STOPWORDS:
                continue
            counter[word] += item.get("weight", 1.0)

    return [word for word, _ in counter.most_common(top_n)]
