import datetime as dt
import re
import textwrap

WIDTH = 72
RULE = "-" * WIDTH


def _wrap(text: str, indent: str = "   "):
    return textwrap.fill(" ".join(text.split()), WIDTH, initial_indent=indent, subsequent_indent=indent)


def _title(i: int, title: str):
    return _wrap(f"{i}. {title}", indent="").replace("\n", "\n   ")


def _short(text: str, max_chars: int = 320):
    """First couple of sentences, cut at a sentence boundary when possible."""
    text = " ".join(text.split())
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for s in sentences:
        if len(out) + len(s) > max_chars:
            break
        out += s + " "
    return out.strip() or text[:max_chars].rstrip() + "..."


def _section(name: str, count: int):
    return [RULE, f"{name} ({count})", RULE, ""]


def build_digest(news, feed_items, papers, summaries=None, intro=None, errors=None):
    summaries = summaries or {}
    today = dt.date.today().strftime("%A, %B %d, %Y")
    lines = [
        f"YOUR DAILY TECH DIGEST - {today}",
        "AI / ML, quantum computing and programming, the last 24 hours.",
        "",
    ]
    if intro:
        lines += [_wrap(intro, indent=""), ""]

    if news:
        lines += _section("TOP NEWS", len(news))
        for i, (topic, s) in enumerate(news, 1):
            lines.append(_title(i, s["title"]))
            lines.append(f"   [{topic}] {s['points']} points, {s['comments']} comments")
            lines.append(f"   {s['url']}")
            if s["url"] != s["discussion"]:
                lines.append(f"   Discussion: {s['discussion']}")
            lines.append("")

    if feed_items:
        lines += _section("FROM THE FEEDS", len(feed_items))
        for i, (topic, item) in enumerate(feed_items, 1):
            lines.append(_title(i, item["title"]))
            lines.append(f"   [{topic}] {item['source']}")
            summary = summaries.get(item["url"]) or _short(item["summary"], 240)
            if summary:
                lines.append("")
                lines.append(_wrap(summary))
            lines.append("")
            lines.append(f"   {item['url']}")
            lines.append("")

    if papers:
        lines += _section("NEW PAPERS", len(papers))
        for i, (topic, p) in enumerate(papers, 1):
            authors = ", ".join(a.name for a in p.authors[:3]) + (" et al." if len(p.authors) > 3 else "")
            lines.append(_title(i, p.title))
            lines.append(_wrap(f"[{topic}] {authors}"))
            lines.append("")
            lines.append(_wrap(summaries.get(p.entry_id) or _short(p.summary)))
            lines.append("")
            lines.append(f"   {p.entry_id}")
            lines.append("")

    lines += [RULE, "That's it for today. See you tomorrow.", ""]

    if errors:
        lines += ["Some sources failed today:"] + [f" - {e}" for e in errors] + [""]

    return "\n".join(lines)
