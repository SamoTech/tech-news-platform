# modules/writer/templates.py

from typing import Dict
from datetime import datetime
from html import escape


def render_article(
    title: str,
    sections: Dict[str, str],
    angle: str,
    author: str = "GlobalTechDigest Editorial Team",
    date: str | None = None,
) -> str:
    """
    Render a full HTML article using structured sections.
    This is the single authoritative HTML layout for the platform.
    """

    date = date or datetime.utcnow().strftime("%B %d, %Y")

    def section_html(section_id: str, heading: str, body: str) -> str:
        return f"""
  <section id="{escape(section_id)}">
    <h2>{escape(heading)}</h2>
    <p>{body}</p>
  </section>
"""

    html = f"""<article>
  <header>
    <h1>{escape(title)}</h1>
    <p><em>By {escape(author)} • {escape(date)}</em></p>
  </header>
"""

    # Mandatory EEAT / AdSense-safe structure
    ordered_sections = [
        ("introduction", "Introduction"),
        ("analysis", "Analysis"),
        ("implications", "Implications"),
        ("key_takeaways", "Key Takeaways"),
        ("conclusion", "Conclusion"),
    ]

    for key, heading in ordered_sections:
        content = sections.get(key)
        if content:
            html += section_html(key, heading, content)

    html += """
</article>
"""
    return html.strip()
