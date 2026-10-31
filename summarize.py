import json
import re
import urllib.request

from config import OLLAMA_MODEL, OLLAMA_URL

PAPER_PROMPT = """Summarize this research paper for a busy software engineer in EXACTLY 2 short sentences
(under 50 words total): what they did, then why it matters. Plain words, no hype.
Start directly with the content, e.g. "Researchers built..." or "A new benchmark...", never "This paper".

Title: {title}
Abstract: {text}"""

ARTICLE_PROMPT = """Rewrite this news excerpt as 1-2 short sentences (under 45 words total) that tell a
software engineer what happened. Only use facts from the excerpt. Plain words, no hype, no preamble.

Title: {title}
Excerpt: {text}"""

NEWS_PROMPT = """Summarize this article in 1-2 short sentences (under 45 words total) that tell a
software engineer what it is about. Only use facts from the text. Plain words, no hype, no preamble.
The text was scraped from a web page: ignore menus, cookie banners and subscription prompts, and never
comment on the text itself.

Title: {title}
Text: {text}"""

INTRO_PROMPT = """You write the opening of a friendly daily tech newsletter for one reader.
Here are today's headlines:

{headlines}

Write 2-3 relaxed, conversational sentences that tease the most interesting ones.
Only mention things that appear in the headlines; do not invent details. No greeting,
no sign-off, no call to action like "stay tuned", no lists, no emojis."""


def ollama_available():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as r:
            models = [m["name"] for m in json.load(r)["models"]]
        return any(m.split(":")[0] == OLLAMA_MODEL.split(":")[0] for m in models)
    except OSError:
        return False


def _first_sentences(text: str, n: int):
    """Small models don't always respect length limits, so enforce it."""
    sentences = re.split(r"(?<=[.!?])(?<!e\.g\.)(?<!i\.e\.)(?<!et al\.)(?<!vs\.)\s+(?=[A-Z])", text)
    return " ".join(sentences[:n])


def _drop_meta_comments(text: str):
    """Remove sentences where the model talks about its input ("No information ... in the given text")."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    kept = [x for x in sentences if not re.search(r"\b(?:given|provided) (?:text|excerpt|article)\b|\bin the (?:text|excerpt)\b", x, re.I)]
    return " ".join(kept) or text


def generate(prompt: str, max_sentences: int, max_tokens: int = 150):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": max_tokens},
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    # Generous timeout: on a CPU-only machine (GitHub Actions) the first call also loads the model
    with urllib.request.urlopen(req, timeout=300) as r:
        text = json.load(r)["response"].strip()
    text = re.sub(r'^["\']|["\']$', "", " ".join(text.split()))
    return _first_sentences(_drop_meta_comments(text), max_sentences)


def enrich(news, feed_items, papers):
    """LLM extras for the digest: ({url: summary}, intro or None). Empty if Ollama isn't running."""
    if not ollama_available():
        print("Ollama not available, using abstracts/excerpts as summaries")
        return {}, None

    summaries = {}
    jobs = [(s["url"], NEWS_PROMPT, s["title"], s["text"]) for _, s in news if s.get("text")]
    jobs += [(p.entry_id, PAPER_PROMPT, p.title, p.summary) for _, p in papers]
    jobs += [(f["url"], ARTICLE_PROMPT, f["title"], f["summary"]) for _, f in feed_items if f["summary"]]

    for i, (key, prompt, title, text) in enumerate(jobs, 1):
        print(f"Summarizing {i}/{len(jobs)}: {title[:60]}")
        try:
            summaries[key] = generate(prompt.format(title=title, text=" ".join(text.split())), max_sentences=2)
        except OSError as e:
            print(f"  skipped ({e}); falling back to the original text")

    headlines = [s["title"] for _, s in news[:6]] + [f["title"] for _, f in feed_items[:4]]
    headlines += [p.title for _, p in papers[:3]]
    try:
        intro = generate(INTRO_PROMPT.format(headlines="\n".join(f"- {h}" for h in headlines)), 3, 160)
    except OSError:
        intro = None
    if intro:
        # Drop a tacked-on sign-off like "Stay curious!"
        intro = re.sub(r"(?<=[.!?])\s+(?:\S+\s+){0,3}\S+!$", "", intro)

    return summaries, intro
