import json

import yfinance as yf

from config import (
    TICKERS, START_DATE, END_DATE, INITIAL_CASH, COMMISSION, SLIPPAGE,
    EARNINGS_FILE, SCREENER_TOP_N, STOP_LOSS_PCT, USE_REGIME_FILTER, REGIME_MA_DAYS,
)

from data.downloader import download_multiple_stocks
from data.earnings_loader import load_earnings_events
from strategies.post_earnings_drift import PostEarningsDriftStrategy
from backtesting.backtester import Backtester
from backtesting.portfolio_backtester import PortfolioBacktester
from analytics.metrics import print_metrics
from optimizer import walk_forward_pead
from screener import screen_pead_tickers, print_screening_results
from utils.plotting import drift_plot_price_and_signals, plot_portfolio, plot_portfolio_combined


def fetch_spy_closes(start, end):
    spy = yf.download('SPY', start=start, end=end, auto_adjust=True, progress=False)
    return spy['Close'].squeeze()


def main():
    stock_data = download_multiple_stocks(TICKERS, START_DATE, END_DATE)

    all_earnings = {
        ticker: load_earnings_events(EARNINGS_FILE, ticker)
        for ticker in TICKERS
    }

    print('Fetching SPY for market regime filter...')
    spy_closes = fetch_spy_closes(START_DATE, END_DATE)

    print('Screening tickers...')
    qualified, all_results = screen_pead_tickers(
        stock_data, all_earnings, INITIAL_CASH,
        top_n=SCREENER_TOP_N,
    )
    print_screening_results(qualified, all_results)

    with open('qualified_tickers.json', 'w') as f:
        json.dump(qualified, f, indent=2)
    print(f'\nSaved {len(qualified)} qualified tickers to qualified_tickers.json')

    if not qualified:
        print('\nNo tickers passed the screen.')
        return

    # --- Walk-forward validation ---
    print('\n\n=== Walk-Forward Validation (60% train / 40% out-of-sample) ===')
    wf_header = f"  {'Ticker':<8} {'Train Sharpe':>13} {'OOS Sharpe':>11} {'OOS Return':>11} {'OOS Alpha':>10} {'Train ends':>12}"
    print(wf_header)
    print('  ' + '-' * (len(wf_header) - 2))

    qualified_with_wf = []
    for r in qualified:
        ticker = r['ticker']
        wf = walk_forward_pead(
            stock_data[ticker], all_earnings[ticker], INITIAL_CASH,
            stop_loss_pct=STOP_LOSS_PCT,
        )
        if wf is None:
            print(f"  {ticker:<8} {'insufficient data':>13}")
            continue
        print(f"  {ticker:<8} {wf['train_sharpe']:>13.2f} {wf['oos_sharpe']:>11.2f} "
              f"{wf['oos_return']:>+11.2%} {wf['oos_alpha']:>+10.2%} {wf['train_end']:>12}")
        qualified_with_wf.append(r)

    # --- Generate signals with regime filter and stop loss ---
    all_signals = {}
    surprise_map = {}
    for r in qualified_with_wf:
        ticker = r['ticker']
        strategy = PostEarningsDriftStrategy(
            all_earnings[ticker], r['threshold'], r['hold_days'],
            regime_data=spy_closes if USE_REGIME_FILTER else None,
            regime_ma_days=REGIME_MA_DAYS,
        )
        all_signals[ticker] = strategy.generate_signals(stock_data[ticker])

        # Build surprise map: use the mean surprise across all events for sizing
        events = all_earnings[ticker]
        if not events.empty:
            surprise_map[ticker] = float(events['surprise'].abs().mean())

    if not all_signals:
        print('\nNo tickers remaining after walk-forward filter.')
        return

    # --- Individual backtests ---
    print(f'\n\nIndividual results ({len(all_signals)} tickers, with regime filter + stop loss):')
    for r in qualified_with_wf:
        ticker = r['ticker']
        stop_str = f'{STOP_LOSS_PCT:.0%}' if STOP_LOSS_PCT else 'none'
        print(f'\n--- {ticker} (threshold={r["threshold"]}, hold={r["hold_days"]}d, stop={stop_str}) ---')
        backtester = Backtester(INITIAL_CASH, COMMISSION, SLIPPAGE, stop_loss_pct=STOP_LOSS_PCT)
        results, trades = backtester.run(all_signals[ticker])
        print_metrics(results, trades)
        drift_plot_price_and_signals(results, ticker)
        plot_portfolio(results, ticker)

    # --- Portfolio backtest ---
    print('\n\n=== Combined Portfolio ===')
    port_backtester = PortfolioBacktester(INITIAL_CASH, COMMISSION, SLIPPAGE, stop_loss_pct=STOP_LOSS_PCT)
    port_results, port_trades = port_backtester.run(all_signals, surprise_map=surprise_map)
    print_metrics(port_results, port_trades)
    plot_portfolio_combined(port_results, list(all_signals.keys()))


if __name__ == '__main__':
    main()
