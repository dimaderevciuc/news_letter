from config import TOPICS


def topic_scores(text: str):
    text = f" {text.lower()} "
    return {topic: sum(text.count(kw) for kw in kws) for topic, kws in TOPICS.items()}


def best_topic(text: str):
    scores = topic_scores(text)
    topic = max(scores, key=scores.get)
    return topic, scores[topic]


def rank_papers(papers, top_n: int):
    """Keyword-score papers, then pick round-robin across topics so no topic crowds out the rest."""
    buckets = {topic: [] for topic in TOPICS}
    for p in papers:
        # Title hits count triple: a keyword in the title is a much stronger signal
        topic, score = best_topic(f"{p.title} {p.title} {p.title} {p.summary}")
        if score > 0:
            buckets[topic].append((score, p))

    for items in buckets.values():
        items.sort(key=lambda x: x[0], reverse=True)

    picked = []
    while len(picked) < top_n and any(buckets.values()):
        for topic, items in buckets.items():
            if items and len(picked) < top_n:
                picked.append((topic, items.pop(0)[1]))
    return picked


def rank_news(stories, top_n: int):
    """HN points, boosted when the title matches one of the topics."""
    scored = []
    for s in stories:
        topic, hits = best_topic(s["title"])
        scored.append((s["points"] * (1 + hits), topic if hits else "General", s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(topic, s) for _, topic, s in scored[:top_n]]


def rank_feed_items(items, top_n: int):
    """Newest first within each feed topic, picked round-robin so every topic gets a slot."""
    buckets = {topic: [] for topic in TOPICS}
    for item in sorted(items, key=lambda i: i["published"], reverse=True):
        buckets.setdefault(item["topic"], []).append(item)

    picked = []
    while len(picked) < top_n and any(buckets.values()):
        for topic, bucket in buckets.items():
            if bucket and len(picked) < top_n:
                picked.append((topic, bucket.pop(0)))
    return picked
