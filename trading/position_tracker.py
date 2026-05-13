"""
Tracks open PEAD positions in a local JSON file so the live trader knows
when each position was entered and how long to hold it.
"""

import json
import os
import numpy as np
from datetime import date

TRACKER_FILE = os.path.join(os.path.dirname(__file__), 'positions.json')


def load():
    if not os.path.exists(TRACKER_FILE):
        return {}
    with open(TRACKER_FILE) as f:
        return json.load(f)


def save(positions):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(positions, f, indent=2)


def add(ticker, dollars_allocated, entry_price, hold_days):
    positions = load()
    positions[ticker] = {
        'entry_date':        str(date.today()),
        'dollars_allocated': round(dollars_allocated, 2),
        'entry_price':       round(entry_price, 4),
        'hold_days':         hold_days,
    }
    save(positions)


def remove(ticker):
    positions = load()
    positions.pop(ticker, None)
    save(positions)


def positions_to_exit():
    """Returns list of (ticker, position_dict) where hold_days trading days have elapsed."""
    positions = load()
    today = np.busday_offset(str(date.today()), 0, roll='forward')
    to_exit = []
    for ticker, pos in positions.items():
        entry = np.busday_offset(pos['entry_date'], 0, roll='forward')
        trading_days_held = np.busday_count(entry, today)
        if trading_days_held >= pos['hold_days']:
            to_exit.append((ticker, pos))
    return to_exit


def print_positions():
    positions = load()
    if not positions:
        print('  No open positions tracked.')
        return
    today = np.busday_offset(str(date.today()), 0, roll='forward')
    print(f"  {'Ticker':<8} {'Entry':>12} {'Allocated':>10} {'Days Held':>10} {'Hold Target':>12}")
    print('  ' + '-' * 56)
    for ticker, pos in positions.items():
        entry = np.busday_offset(pos['entry_date'], 0, roll='forward')
        days_held = int(np.busday_count(entry, today))
        print(f"  {ticker:<8} {pos['entry_date']:>12} ${pos['dollars_allocated']:>9.2f} "
              f"{days_held:>10} {pos['hold_days']:>12}")
