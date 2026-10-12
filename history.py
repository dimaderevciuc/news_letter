import datetime as dt
import json
from pathlib import Path

from config import HISTORY_DAYS, HISTORY_FILE

PATH = Path(__file__).parent / HISTORY_FILE


def load_sent():
    """{url: date sent} for everything emailed in the last HISTORY_DAYS days."""
    if not PATH.exists():
        return {}
    cutoff = (dt.date.today() - dt.timedelta(days=HISTORY_DAYS)).isoformat()
    return {url: day for url, day in json.loads(PATH.read_text()).items() if day >= cutoff}


def mark_sent(urls):
    sent = load_sent()
    today = dt.date.today().isoformat()
    sent.update({url: today for url in urls})
    PATH.write_text(json.dumps(sent, indent=1, sort_keys=True))
