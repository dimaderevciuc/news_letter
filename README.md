# Daily Tech Digest

A personal plain-text newsletter: every morning it collects the last 24 hours of
AI / ML, quantum computing and programming news and papers, picks the best ones
and emails them to you.

**Sources**
- Hacker News: top stories, boosted when they match your topics
- RSS feeds: quantum, AI and programming blogs/news (`FEEDS` in `config.py`)
- arXiv: newest papers in cs.AI, cs.LG, cs.CL, cs.CV, cs.SE, cs.PL, quant-ph

## Setup

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env   # then fill in your Gmail address and App Password
```

## Usage

```bash
.venv/bin/python main.py          # print the digest (nothing is sent or remembered)
.venv/bin/python main.py --send   # email it and remember what was sent
```

Items that were emailed are stored in `sent_history.json` for 14 days so they
never appear twice. Delete that file to reset.

## Customizing

Everything lives in `config.py`:
- `TOPICS`: the keywords that decide what counts as relevant, and the topic groups the digest balances across
- `FEEDS`: RSS/Atom feeds and the topic each belongs to
- `TOP_NEWS`, `TOP_FEED_ITEMS`, `TOP_PAPERS`: how many items per section
- `HN_MIN_POINTS`: minimum Hacker News points for a story to be considered

## Better paper summaries (optional)

If [Ollama](https://ollama.com) is running with the model from `OLLAMA_MODEL`,
the picked papers get a 2-sentence summary written by the model instead of the
first lines of the abstract. Without Ollama the digest still works.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b
```

## Send it every morning

A systemd user timer runs it daily at 07:30, or as soon as the laptop wakes up
if it was off at that time:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/digest.service deploy/digest.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now digest.timer

systemctl --user list-timers digest.timer   # check the next run
systemctl --user start digest.service       # send one right now
journalctl --user -u digest.service         # see logs / errors
```

To change the time, edit `OnCalendar=` in `digest.timer` and repeat the copy and `daemon-reload`.
