import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), 'activity.json')
MAX_ENTRIES = 200


def log(action, ticker=None, details='', dry_run=True):
    entries = _load()
    entries.insert(0, {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'action':    action,
        'ticker':    ticker,
        'details':   details,
        'dry_run':   dry_run,
    })
    _save(entries[:MAX_ENTRIES])


def get_recent(n=50):
    return _load()[:n]


def _load():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def _save(entries):
    with open(LOG_FILE, 'w') as f:
        json.dump(entries, f, indent=2)
