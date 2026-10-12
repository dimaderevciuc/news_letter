import datetime as dt
import json
import urllib.parse
import urllib.request

from config import HN_MIN_POINTS, LOOKBACK_HOURS

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


def fetch_hacker_news():
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=LOOKBACK_HOURS)
    params = urllib.parse.urlencode({
        "tags": "story",
        "numericFilters": f"created_at_i>{int(since.timestamp())},points>={HN_MIN_POINTS}",
        "hitsPerPage": 200,
    })

    with urllib.request.urlopen(f"{HN_SEARCH_URL}?{params}", timeout=30) as r:
        hits = json.load(r)["hits"]

    return [
        {
            "title": h["title"],
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
            "discussion": f"https://news.ycombinator.com/item?id={h['objectID']}",
            "points": h.get("points", 0),
            "comments": h.get("num_comments", 0),
        }
        for h in hits
    ]
