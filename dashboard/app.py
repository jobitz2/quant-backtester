import json
import os
import sys

import numpy as np
import yfinance as yf
from flask import Flask, jsonify, render_template

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from trading import activity_log, position_tracker as tracker
from config import DRY_RUN, INITIAL_CASH

app = Flask(__name__)

QUALIFIED_FILE = os.path.join(os.path.dirname(__file__), '..', 'qualified_tickers.json')


def _load_qualified():
    if not os.path.exists(QUALIFIED_FILE):
        return []
    with open(QUALIFIED_FILE) as f:
        return json.load(f)


def _current_price(ticker):
    try:
        quotes = yf.Ticker(ticker).fast_info
        return float(quotes['last_price'])
    except Exception:
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/positions')
def api_positions():
    positions = tracker.load()
    today = np.busday_offset(str(__import__('datetime').date.today()), 0, roll='forward')
    rows = []
    total_allocated = 0.0
    total_current = 0.0

    for ticker, pos in positions.items():
        entry = np.busday_offset(pos['entry_date'], 0, roll='forward')
        days_held = int(np.busday_count(entry, today))
        price = _current_price(ticker)
        allocated = pos['dollars_allocated']
        current_value = (price / pos['entry_price']) * allocated if price else None
        pnl = current_value - allocated if current_value is not None else None
        pnl_pct = pnl / allocated if pnl is not None else None

        total_allocated += allocated
        if current_value:
            total_current += current_value

        rows.append({
            'ticker':        ticker,
            'entry_date':    pos['entry_date'],
            'days_held':     days_held,
            'hold_target':   pos['hold_days'],
            'allocated':     round(allocated, 2),
            'entry_price':   pos['entry_price'],
            'current_price': round(price, 2) if price else None,
            'current_value': round(current_value, 2) if current_value else None,
            'pnl':           round(pnl, 2) if pnl is not None else None,
            'pnl_pct':       round(pnl_pct * 100, 2) if pnl_pct is not None else None,
        })

    return jsonify({
        'positions':       rows,
        'total_allocated': round(total_allocated, 2),
        'total_current':   round(total_current, 2),
        'total_pnl':       round(total_current - total_allocated, 2),
    })


@app.route('/api/qualified')
def api_qualified():
    return jsonify(_load_qualified())


@app.route('/api/activity')
def api_activity():
    return jsonify(activity_log.get_recent(50))


@app.route('/api/summary')
def api_summary():
    qualified = _load_qualified()
    positions = tracker.load()
    activity = activity_log.get_recent(1)
    last_run = activity[0]['timestamp'] if activity else None
    return jsonify({
        'dry_run':          DRY_RUN,
        'initial_cash':     INITIAL_CASH,
        'num_qualified':    len(qualified),
        'num_positions':    len(positions),
        'last_run':         last_run,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5050)
