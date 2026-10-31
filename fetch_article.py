"""Reads the text of a linked article so the LLM can summarize Hacker News stories,
which come with only a title and a link."""

import html
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

MAX_BYTES = 2_000_000
# Kept short so prompts stay fast on the CPU-only GitHub runner
MAX_CHARS = 2500

# Signup / cookie / legal paragraphs that otherwise end up in the summary
BOILERPLATE = re.compile(
    r"subscri(?:be|ption|bers)|newsletter|inbox|sign up|cookies?\b|privacy policy|terms of (?:service|use)|all rights reserved",
    re.I,
)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; daily-digest/1.0)", "Accept": "text/html"}


def html_to_text(fragment: str):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _meta_description(page: str):
    for name in ("og:description", "description", "twitter:description"):
        m = re.search(rf'<meta[^>]+(?:property|name)=["\']{name}["\'][^>]*content=["\']([^"\']+)', page, re.I)
        if m:
            return html_to_text(m.group(1))
    return ""


def read_article(url: str):
    """(description, body text) of a web page; empty strings if it can't be read (paywall, PDF, blocked...)."""
    if url.lower().endswith(".pdf"):
        return "", ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            if "html" not in r.headers.get("Content-Type", ""):
                return "", ""
            raw = r.read(MAX_BYTES)
            charset = r.headers.get_content_charset() or "utf-8"
    except (OSError, ValueError):
        return "", ""

    page = raw.decode(charset, errors="replace")
    description = _meta_description(page)
    page = re.sub(r"<(script|style|nav|header|footer|aside|form)\b.*?</\1>", " ", page, flags=re.S | re.I)
    # Paragraphs of real prose; short ones are usually menus, captions or cookie notices
    paragraphs = [html_to_text(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", page, flags=re.S | re.I)]
    body = " ".join(p for p in paragraphs if len(p) >= 60 and not BOILERPLATE.search(p))[:MAX_CHARS]
    return description, body


def add_article_text(stories):
    """Fills story["excerpt"] (page description) and story["text"] (what the LLM summarizes), in parallel."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(lambda s: read_article(s["url"]) if not s.get("text") else ("", s["text"]), stories)
        for s, (description, body) in zip(stories, results):
            s["excerpt"] = description
            s["text"] = s.get("text") or body or description
