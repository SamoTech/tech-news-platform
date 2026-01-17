def build_post(article_text, trends):
    lines = article_text.split("\n")
    title = lines[2] if len(lines) > 2 else "Latest Tech Developments"

    meta_description = (
        "A closer look at recent technology developments shaping the industry today."
    )

    keywords = ", ".join(trends[:5]) if trends else "technology, tech news, innovation"

    return {
        "title": title.strip(),
        "meta_description": meta_description,
        "keywords": keywords,
        "content": article_text.strip()
    }
