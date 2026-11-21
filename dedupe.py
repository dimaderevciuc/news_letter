"""Drops items that cover the same event under a different link and a different title.

Hacker News often has two submissions of one story (the paper itself and a blog post or
announcement about it). Their URLs differ, so the URL history can't catch them, and their
titles can share no words at all ("X claims proof of the GRH [pdf]" vs "Hurried announcement: Y GRH").
What they do share are rare words in their text: names, project names, the specific topic.

So every item becomes a set of words from its title and text, each word weighted by how rare
it is in today's batch (IDF). Two items are the same story when
  1. the words they share make up a large part of the weight of the shorter one, and
  2. at least two of those shared words come from a headline. Two different model launches share
     plenty of body words ("model", "reasoning", "benchmarks") but not their headline subject.
"""

import math
import re
import unicodedata
from collections import Counter

# How much of the shorter item's (IDF-weighted) words must be shared to call it a duplicate
THRESHOLD = 0.4
# Fewer shared words than this is never a duplicate, however short the items are
MIN_SHARED_WORDS = 3
# How many of the shared words must appear in one of the two headlines
MIN_SHARED_HEADLINE_WORDS = 2
# Only the start of the article text: that's where the who/what is, and it keeps long pages from matching everything
TEXT_CHARS = 1500

STOPWORDS = set("""
a about after again against all also an and any are as at be because been before being between both but by
can could did do does doing down during each few for from further had has have having he her here hers him
his how if in into is it its just more most new no nor not now of off on once only or other our out over own
same she should so some such than that the their them then there these they this those through to too under
until up very was we were what when where which while who whom why will with would you your
says said show hn ask pdf video via using use used get got make made one two first last year years today
""".split())


def _fold(text: str):
    """Lowercase and strip accents, so "Alpöge" and "Alpoge" are the same word."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def _words(title: str, text: str):
    words = re.findall(r"[a-z0-9][a-z0-9+#.-]*[a-z0-9+#]|[a-z0-9]", _fold(f"{title} {text[:TEXT_CHARS]}"))
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS and not w.isdigit()}


def _same_story(a: set, b: set, a_title: set, b_title: set, idf: dict):
    shared = a & b
    if len(shared) < MIN_SHARED_WORDS or len(shared & (a_title | b_title)) < MIN_SHARED_HEADLINE_WORDS:
        return False
    weight = lambda words: sum(idf[w] for w in words)
    smaller = min(weight(a), weight(b))
    return smaller > 0 and weight(shared) / smaller >= THRESHOLD


def drop_duplicates(news, feed_items):
    """Keeps the first (best ranked) item of every story; news wins over feed items.

    Takes and returns the (topic, item) lists from rank.py, plus the URLs that were dropped.
    """
    entries = [("news", t, s, _words(s["title"], s.get("text") or s.get("excerpt", ""))) for t, s in news]
    entries += [("feed", t, f, _words(f["title"], f.get("summary", ""))) for t, f in feed_items]
    titles = {id(item): _words(item["title"], "") for _, _, item, _ in entries}

    # Inverse document frequency over today's batch: words most items use ("model", "release") weigh ~0
    df = Counter(w for *_, words in entries for w in words)
    idf = {w: math.log(len(entries) / n) for w, n in df.items()}

    kept, dropped = [], []
    for kind, topic, item, words in entries:
        twin = next(
            (k for k in kept if _same_story(words, k[3], titles[id(item)], titles[id(k[2])], idf)),
            None,
        )
        if twin:
            print(f"Duplicate dropped: {item['title'][:60]!r} (same story as {twin[2]['title'][:60]!r})")
            dropped.append(item["url"])
        else:
            kept.append((kind, topic, item, words))

    news = [(t, i) for kind, t, i, _ in kept if kind == "news"]
    feed_items = [(t, i) for kind, t, i, _ in kept if kind == "feed"]
    return news, feed_items, dropped
