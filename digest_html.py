"""HTML version of the digest. Email clients are picky: layout is tables + inline styles,
and the <style> block only adds dark mode for clients that support it (Apple Mail, iOS, some Outlook)."""

import datetime as dt
from html import escape

from digest import _short

SERIF = "Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

TOPIC_COLORS = {
    "AI / ML": "#5b4bdb",
    "Quantum": "#0f8b8d",
    "Programming": "#c2410c",
    "General": "#6b7280",
}

DARK_MODE_CSS = """
:root { color-scheme: light dark; supported-color-schemes: light dark; }
@media (prefers-color-scheme: dark) {
  .bg { background: #141619 !important; }
  .card { background: #1d2024 !important; }
  .t { color: #ece9e4 !important; }
  .b { color: #c9c6c0 !important; }
  .m { color: #9a9fa6 !important; }
  .rule { border-color: #2c3036 !important; }
}
"""


def _link(url: str, label: str, color: str):
    return (f'<a href="{escape(url)}" style="color:{color};text-decoration:none;'
            f'font:600 14px/1.4 {SANS};">{escape(label)}&nbsp;&rarr;</a>')


def _item(topic: str, meta: str, title: str, url: str, summary: str = "", links=(), lead=False, first=False):
    color = TOPIC_COLORS.get(topic, TOPIC_COLORS["General"])
    size = 21 if lead else 18
    border = "" if first else "border-top:1px solid #ece7dd;"
    parts = [
        f'<tr><td class="rule" style="padding:20px 0;{border}">',
        f'<div style="font:700 11px/1.4 {SANS};letter-spacing:.08em;text-transform:uppercase;color:{color};">'
        f'{escape(topic)}<span class="m" style="color:#8a8f96;font-weight:500;letter-spacing:.02em;'
        f'text-transform:none;">&nbsp;&middot;&nbsp;{escape(meta)}</span></div>',
        f'<a href="{escape(url)}" class="t" style="display:block;margin-top:6px;font:700 {size}px/1.35 {SERIF};'
        f'color:#1d2125;text-decoration:none;">{escape(title)}</a>',
    ]
    if summary:
        parts.append(f'<p class="b" style="margin:8px 0 0;font:16px/1.6 {SANS};color:#41464d;">{escape(summary)}</p>')
    if links:
        parts.append('<div style="margin-top:10px;">'
                     + "&nbsp;&nbsp;&nbsp;".join(_link(u, label, color) for label, u in links) + "</div>")
    parts.append("</td></tr>")
    return "".join(parts)


def _section(title: str, subtitle: str, rows):
    return f"""
<tr><td style="padding:0 0 20px;">
 <table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="card"
        style="background:#ffffff;border-radius:14px;">
  <tr><td style="padding:28px 28px 8px;">
   <div class="t" style="font:700 24px/1.2 {SERIF};color:#1d2125;">{escape(title)}</div>
   <div class="m" style="margin-top:4px;font:14px/1.5 {SANS};color:#8a8f96;">{escape(subtitle)}</div>
  </td></tr>
  <tr><td style="padding:0 28px 12px;">
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{"".join(rows)}</table>
  </td></tr>
 </table>
</td></tr>"""


def build_html(news, feed_items, papers, summaries=None, intro=None, errors=None, minutes=5):
    summaries = summaries or {}
    today = dt.date.today().strftime("%A, %B %-d")
    preheader = intro or (news[0][1]["title"] if news else "Your daily AI, quantum and programming digest")

    sections = []

    if intro:
        sections.append(f"""
<tr><td style="padding:0 0 20px;">
 <table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="card"
        style="background:#ffffff;border-radius:14px;">
  <tr><td style="padding:26px 28px;">
   <p class="t" style="margin:0;font:italic 19px/1.6 {SERIF};color:#1d2125;">{escape(intro)}</p>
  </td></tr>
 </table>
</td></tr>""")

    if news:
        rows = []
        for i, (topic, s) in enumerate(news):
            links = [("Read", s["url"])]
            if s["url"] != s["discussion"]:
                links.append(("Discussion", s["discussion"]))
            summary = summaries.get(s["url"]) or _short(s.get("excerpt", ""), 240)
            rows.append(_item(
                topic, f"{s['points']} points · {s['comments']} comments", s["title"], s["url"],
                summary, links, lead=i < 3, first=i == 0,
            ))
        sections.append(_section("Top stories", "What the tech world is talking about today", rows))

    if feed_items:
        rows = [
            _item(topic, f["source"], f["title"], f["url"],
                  summaries.get(f["url"]) or _short(f["summary"], 240), first=i == 0)
            for i, (topic, f) in enumerate(feed_items)
        ]
        sections.append(_section("Worth reading", "From the blogs and newsrooms you follow", rows))

    if papers:
        rows = []
        for i, (topic, p) in enumerate(papers):
            authors = ", ".join(a.name for a in p.authors[:3]) + (" et al." if len(p.authors) > 3 else "")
            links = [("Abstract", p.entry_id)] + ([("PDF", p.pdf_url)] if p.pdf_url else [])
            rows.append(_item(topic, authors, p.title, p.entry_id,
                              summaries.get(p.entry_id) or _short(p.summary), links, first=i == 0))
        sections.append(_section("Fresh from arXiv", "New papers worth a look", rows))

    error_note = ""
    if errors:
        error_note = (f'<div class="m" style="margin-top:10px;">Some sources failed today: '
                      f'{escape("; ".join(errors))}</div>')

    return f"""<!doctype html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>The Daily Digest</title><style>{DARK_MODE_CSS}</style>
</head>
<body class="bg" style="margin:0;padding:0;background:#f3efe7;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(preheader)}&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="bg" style="background:#f3efe7;">
<tr><td align="center" style="padding:28px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;">

<tr><td style="padding:4px 6px 22px;">
 <div class="m" style="font:700 12px/1.4 {SANS};letter-spacing:.14em;text-transform:uppercase;color:#8a8f96;">
  {escape(today)} &nbsp;&middot;&nbsp; {minutes} min read</div>
 <div class="t" style="margin-top:6px;font:700 34px/1.15 {SERIF};color:#1d2125;">The Daily Digest</div>
 <div class="b" style="margin-top:6px;font:15px/1.5 {SANS};color:#5c6168;">
  <span style="color:{TOPIC_COLORS['AI / ML']};">AI&nbsp;&amp;&nbsp;ML</span> &nbsp;&middot;&nbsp;
  <span style="color:{TOPIC_COLORS['Quantum']};">Quantum</span> &nbsp;&middot;&nbsp;
  <span style="color:{TOPIC_COLORS['Programming']};">Programming</span></div>
</td></tr>

{"".join(sections)}

<tr><td class="m" style="padding:8px 6px 0;font:13px/1.6 {SANS};color:#8a8f96;">
 That's all for today. See you tomorrow.<br>
 Sources: Hacker News, the blogs and newsrooms in your feed list, and arXiv.
 {error_note}
</td></tr>

</table>
</td></tr>
</table>
</body></html>"""
