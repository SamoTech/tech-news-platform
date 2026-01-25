# modules/writer/internal_links.py

from pathlib import Path
import re


def extract_keywords(text: str, limit: int = 5) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:limit]


def find_related_articles(content: str, drafts_dir: str = "data/drafts") -> list[tuple[str, str]]:
    keywords = extract_keywords(content)
    drafts_path = Path(drafts_dir)

    links = []

    for file in drafts_path.glob("*.html"):
        text = file.read_text(encoding="utf-8").lower()
        for kw in keywords:
            if kw in text:
                title = file.stem.replace("-", " ")
                links.append((title, file.name))
                break

    return links[:3]


def inject_internal_links(content: str) -> str:
    links = find_related_articles(content)
    if not links:
        return content

    block = "<section id=\"internal-links\">\n<h2>Related Articles</h2>\n<ul>\n"
    for title, filename in links:
        block += f"<li><a href=\"/{filename}\">{title}</a></li>\n"
    block += "</ul>\n</section>"

    return content.replace("</article>", block + "\n</article>")
