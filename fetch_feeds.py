import calendar
import datetime as dt
import html
import re
import urllib.request

import feedparser

from config import FEEDS, LOOKBACK_HOURS


def _clean(text: str):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text or "")).split())


def _strip_boilerplate(text: str):
    text = re.sub(r"\s*The post .* appeared first on .*$", "", text)
    return re.sub(r"^Insider Brief\s*", "", text)


def fetch_feeds():
    """Recent entries from every feed in config.FEEDS. Returns (items, errors)."""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=LOOKBACK_HOURS)
    items, errors = [], []

    for url, topic in FEEDS.items():
        try:
            # Downloaded ourselves for the timeout; some servers also send feedparser broken gzip
            req = urllib.request.Request(url, headers={"User-Agent": "daily-digest/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                feed = feedparser.parse(r.read())
        except OSError as e:
            errors.append(f"feed {url}: {e}")
            continue
        if feed.get("bozo") and not feed.entries:
            errors.append(f"feed {url}: {feed.get('bozo_exception')}")
            continue

        source = _clean(feed.feed.get("title", url))
        for e in feed.entries:
            stamp = e.get("published_parsed") or e.get("updated_parsed")
            if not stamp:
                continue
            published = dt.datetime.fromtimestamp(calendar.timegm(stamp), dt.timezone.utc)
            if published < cutoff:
                continue
            items.append({
                "title": _clean(e.get("title", "")),
                "url": e.get("link", ""),
                "source": source,
                "topic": topic,
                "published": published,
                "summary": _strip_boilerplate(_clean(e.get("summary", ""))),
            })

    return items, errors
