# Daily Tech Digest

A personal newsletter: every morning it collects the last 24 hours of AI / ML,
quantum computing and programming news and papers, picks the best ones, has a
local LLM summarize them and emails you a nicely formatted digest (HTML, with a
plain-text version for clients that don't show HTML).

It runs on GitHub Actions, so your laptop doesn't need to be on.

**Sources**
- Hacker News: top stories, boosted when they match your topics (the linked articles are read so they can be summarized)
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
.venv/bin/python main.py                       # print the text digest (nothing sent or remembered)
.venv/bin/python main.py --html digest.html    # also write the HTML email to preview in a browser
.venv/bin/python main.py --send                # email it and remember what was sent
```

Items that were emailed are stored in `sent_history.json` for 14 days so they
never appear twice. Delete that file to reset.

## Customizing

Everything lives in `config.py`:
- `TOPICS`: the keywords that decide what counts as relevant, and the topic groups the digest balances across
- `FEEDS`: RSS/Atom feeds and the topic each belongs to
- `TOP_NEWS`, `TOP_FEED_ITEMS`, `TOP_PAPERS`: how many items per section
- `HN_MIN_POINTS`: minimum Hacker News points for a story to be considered

## LLM summaries

If [Ollama](https://ollama.com) is running with the model from `OLLAMA_MODEL`, it
writes a short opening paragraph for the email plus 1-2 sentence summaries of the
top stories, feed articles and papers. Without Ollama the digest still works and uses the
abstracts / feed excerpts instead.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b
```

## Send it every morning: GitHub Actions (recommended)

`.github/workflows/digest.yml` runs every day on GitHub's servers and emails you at 08:30 Vienna time:
installs Ollama (the model is cached between runs), builds the digest, emails it,
and commits `sent_history.json` back to the repo so nothing repeats.

One-time setup: in the repo on GitHub go to **Settings → Secrets and variables →
Actions → New repository secret** and add `SMTP_USER`, `SMTP_PASSWORD` and
`EMAIL_TO` (same values as your `.env`). Then push.

- Test it: **Actions → Daily digest → Run workflow** (tick *dry run* to only build
  it; the HTML is attached to the run under *Artifacts*).
- Change the time: edit `SEND_AT` / `SEND_TZ` at the top of the workflow. GitHub starts scheduled runs hours late, so the run is triggered at night and waits until then.
- The workflow commits to the repo daily, so run `git pull` before working locally.

## Alternative: run it on this laptop

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
