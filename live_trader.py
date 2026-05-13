"""
Live trader — run this once per trading day at market open.

Dry-run mode (DRY_RUN=True in config.py): logs what it would do, no orders placed.
Live mode  (DRY_RUN=False):               logs in to Robinhood and places real orders.

Setup:
  1. Run main.py to generate qualified_tickers.json from the backtest screener.
  2. Set env vars:  export ROBINHOOD_USERNAME=you@email.com
                    export ROBINHOOD_PASSWORD=yourpassword
  3. Keep DRY_RUN=True until you've verified a few cycles look correct.
  4. Set DRY_RUN=False when ready to go live.
"""

import json
import os
from datetime import date

import pandas as pd
import yfinance as yf

from config import DRY_RUN, INITIAL_CASH
from trading import position_tracker as tracker
from trading import activity_log as log
from trading.robinhood_trader import login, get_buying_power, get_robinhood_positions, place_buy, place_sell, get_current_price

QUALIFIED_FILE = 'qualified_tickers.json'


def load_qualified():
    if not os.path.exists(QUALIFIED_FILE):
        raise FileNotFoundError(
            f"'{QUALIFIED_FILE}' not found. Run main.py first to generate it from the backtest screener."
        )
    with open(QUALIFIED_FILE) as f:
        return {q['ticker']: q for q in json.load(f)}


def get_recent_surprise(ticker, days_back=4):
    """
    Returns the earnings surprise fraction if this ticker reported earnings
    within the last `days_back` calendar days, otherwise None.
    """
    try:
        earnings = yf.Ticker(ticker).earnings_dates
        if earnings is None or earnings.empty:
            return None

        cutoff = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=days_back)
        recent = earnings[earnings.index >= cutoff].dropna(subset=['EPS Estimate', 'Reported EPS'])

        if recent.empty:
            return None

        row = recent.iloc[0]
        estimate = float(row['EPS Estimate'])
        actual   = float(row['Reported EPS'])
        if estimate == 0:
            return None
        return (actual - estimate) / abs(estimate)

    except Exception as e:
        print(f"  Warning: could not fetch earnings for {ticker}: {e}")
        return None


def main():
    mode = '[DRY RUN]' if DRY_RUN else '[LIVE]'
    print(f"=== PEAD Live Trader {mode} — {date.today()} ===\n")

    log.log('RUN', details=f'Trader started in {"dry-run" if DRY_RUN else "live"} mode', dry_run=DRY_RUN)

    qualified = load_qualified()

    # --- Connect to Robinhood ---
    if DRY_RUN:
        buying_power = float(INITIAL_CASH)
        rh_positions = {}
    else:
        login()
        buying_power = get_buying_power()
        rh_positions = get_robinhood_positions()

    print(f"Buying power: ${buying_power:.2f}")

    # --- Current tracked positions ---
    print('\nTracked positions:')
    tracker.print_positions()

    # --- Step 1: Exit positions that have hit their hold target ---
    to_exit = tracker.positions_to_exit()
    print(f'\nExits ({len(to_exit)}):')

    if not to_exit:
        print('  None due today.')

    for ticker, pos in to_exit:
        shares = rh_positions.get(ticker) if not DRY_RUN else pos['dollars_allocated'] / pos['entry_price']
        if shares and shares > 0:
            place_sell(ticker, shares, dry_run=DRY_RUN)
            log.log('SELL', ticker=ticker, details=f'{shares:.4f} shares @ ~${pos["entry_price"]:.2f} entry', dry_run=DRY_RUN)
        else:
            print(f"  {ticker}: no Robinhood position found to sell — removing from tracker anyway")
            log.log('SELL_MISS', ticker=ticker, details='No position found on Robinhood', dry_run=DRY_RUN)
        tracker.remove(ticker)
        if DRY_RUN:
            price = get_current_price(ticker) or pos['entry_price']
            buying_power += shares * price

    # --- Step 2: Scan for new buy signals ---
    open_positions = tracker.load()
    print('\nEarnings scan:')
    new_signals = []

    for ticker, q in qualified.items():
        if ticker in open_positions:
            print(f'  {ticker}: already held, skipping')
            continue

        surprise = get_recent_surprise(ticker)
        if surprise is None:
            print(f'  {ticker}: no recent earnings')
            log.log('SCAN', ticker=ticker, details='No recent earnings', dry_run=DRY_RUN)
            continue

        threshold = q['threshold']
        if surprise >= threshold:
            print(f'  {ticker}: surprise {surprise:+.2%} >= threshold {threshold:.2%} → BUY')
            log.log('SIGNAL', ticker=ticker, details=f'Surprise {surprise:+.2%} >= threshold {threshold:.2%}', dry_run=DRY_RUN)
            new_signals.append(ticker)
        else:
            print(f'  {ticker}: surprise {surprise:+.2%} < threshold {threshold:.2%}, skip')
            log.log('SCAN', ticker=ticker, details=f'Surprise {surprise:+.2%} below threshold {threshold:.2%}', dry_run=DRY_RUN)

    # --- Step 3: Place buy orders ---
    print(f'\nBuys ({len(new_signals)}):')

    if not new_signals:
        print('  No new signals today.')
    elif buying_power < 1.0:
        print('  Insufficient buying power.')
        log.log('SKIP', details='Insufficient buying power for new entries', dry_run=DRY_RUN)
    else:
        alloc = buying_power / len(new_signals)
        for ticker in new_signals:
            price = get_current_price(ticker)
            if price is None:
                print(f'  {ticker}: could not get price, skipping')
                continue
            place_buy(ticker, alloc, dry_run=DRY_RUN)
            tracker.add(ticker, alloc, price, qualified[ticker]['hold_days'])
            log.log('BUY', ticker=ticker, details=f'${alloc:.2f} allocated @ ${price:.2f}, hold {qualified[ticker]["hold_days"]}d', dry_run=DRY_RUN)

    print('\nDone.')


if __name__ == '__main__':
    main()
