import os

LOOKBACK_HOURS = 24
TOP_PAPERS = 10
TOP_NEWS = 10

ARXIV_QUERY = " OR ".join(
    f"cat:{c}"
    for c in ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.SE", "cs.PL", "quant-ph"]
)
ARXIV_MAX_RESULTS = 1000

# Only stories with at least this many points are considered
HN_MIN_POINTS = 30

# Topic -> keywords. Used to score items and to keep the digest balanced across topics.
TOPICS = {
    "AI / ML": [
        "llm", "language model", "transformer", "agent", "reasoning", "diffusion",
        "reinforcement learning", "fine-tun", "benchmark", "openai", "anthropic",
        "claude", "gpt", "gemini", "llama", "mistral", "neural", "machine learning",
        "deep learning", " ai ", "ai-", "inference", "training",
    ],
    "Quantum": [
        "quantum", "qubit", "error correction", "entangle", "superconducting",
        "ion trap", "photonic", "post-quantum",
    ],
    "Programming": [
        "programming", "compiler", "rust", "python", "typescript", "golang", " go ",
        "flutter", "dart", "kotlin", "linux", "database", "open source", "github",
        "code generation", "software engineering", "developer", "api",
        "release", "security", "vulnerability",
    ],
}

# News feeds (RSS/Atom) -> topic. These fill the gaps Hacker News doesn't cover (especially quantum).
FEEDS = {
    "https://thequantuminsider.com/feed/": "Quantum",
    "https://quantumcomputingreport.com/feed/": "Quantum",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed": "AI / ML",
    "https://huggingface.co/blog/feed.xml": "AI / ML",
    "https://openai.com/news/rss.xml": "AI / ML",
    "https://blog.google/technology/ai/rss/": "AI / ML",
    "https://www.quantamagazine.org/computer-science/feed/": "AI / ML",
    "https://github.blog/feed/": "Programming",
    "https://simonwillison.net/atom/everything/": "Programming",
}
TOP_FEED_ITEMS = 8

# Optional: a local Ollama model writes the summaries and the intro. Skipped if Ollama isn't running.
# Both can be overridden with environment variables (the GitHub Actions workflow does this).
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

# Items already emailed are remembered here so they don't show up twice
HISTORY_FILE = "sent_history.json"
HISTORY_DAYS = 14
