import argparse
import datetime as dt
from pathlib import Path

from config import ARXIV_QUERY, TOP_FEED_ITEMS, TOP_NEWS, TOP_PAPERS
from digest import build_digest
from digest_html import build_html
from fetch_arxiv import fetch_arxiv
from fetch_article import add_article_text
from fetch_feeds import fetch_feeds
from fetch_news import fetch_hacker_news
from history import load_sent, mark_sent
from rank import rank_feed_items, rank_news, rank_papers
from send_email import send_email
from summarize import enrich


def fetch(name, fn, errors):
    """Run one fetcher; a failing source is reported in the digest instead of killing the run."""
    try:
        return fn()
    except Exception as e:
        errors.append(f"{name}: {e}")
        return []


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build and send the daily tech digest")
    parser.add_argument("--send", action="store_true", help="email the digest instead of printing it")
    parser.add_argument("--html", metavar="FILE", help="also write the HTML email to FILE to preview it in a browser")
    args = parser.parse_args()

    errors = []
    papers = fetch("arXiv", lambda: fetch_arxiv(ARXIV_QUERY), errors)
    stories = fetch("Hacker News", fetch_hacker_news, errors)
    feed_items, feed_errors = fetch("feeds", fetch_feeds, errors) or ([], [])
    errors += feed_errors
    print(f"Fetched {len(papers)} papers, {len(stories)} stories, {len(feed_items)} feed items")

    # Drop anything already emailed in a previous digest
    sent = load_sent()
    papers = [p for p in papers if p.entry_id not in sent]
    stories = [s for s in stories if s["url"] not in sent]
    feed_items = [f for f in feed_items if f["url"] not in sent]

    news = rank_news(stories, TOP_NEWS)
    add_article_text([s for _, s in news])
    picked_feed = rank_feed_items(feed_items, TOP_FEED_ITEMS)
    picked_papers = rank_papers(papers, TOP_PAPERS)
    summaries, intro = enrich(news, picked_feed, picked_papers)

    body = build_digest(news, picked_feed, picked_papers, summaries, intro, errors)
    minutes = max(1, round(len(body.split()) / 230))
    html = build_html(news, picked_feed, picked_papers, summaries, intro, errors, minutes)
    if args.html:
        Path(args.html).write_text(html)
        print(f"HTML preview written to {args.html}")

    if args.send:
        if not (news or picked_feed or picked_papers):
            raise SystemExit("Nothing to send today: " + "; ".join(errors))
        send_email(f"The Daily Digest - {dt.date.today():%b %-d}", body, html)
        mark_sent(
            [s["url"] for _, s in news]
            + [f["url"] for _, f in picked_feed]
            + [p.entry_id for _, p in picked_papers]
        )
        print("Sent.")
    else:
        print(body)
