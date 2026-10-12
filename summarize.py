import json
import urllib.request

from config import OLLAMA_MODEL, OLLAMA_URL

PROMPT = """Summarize this research paper for a busy software engineer in 2 short, plain sentences:
what they did and why it matters. No hype, no preamble.

Title: {title}
Abstract: {abstract}"""


def ollama_available():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as r:
            models = [m["name"] for m in json.load(r)["models"]]
        return any(m.split(":")[0] == OLLAMA_MODEL.split(":")[0] for m in models)
    except OSError:
        return False


def summarize(title: str, abstract: str):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": PROMPT.format(title=title, abstract=" ".join(abstract.split())),
        "stream": False,
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["response"].strip()


def summarize_papers(papers):
    """{entry_id: summary} for the picked papers, or {} if Ollama isn't running."""
    if not ollama_available():
        return {}
    summaries = {}
    for _, p in papers:
        try:
            summaries[p.entry_id] = summarize(p.title, p.summary)
        except OSError:
            pass  # the digest falls back to the abstract for this paper
    return summaries
