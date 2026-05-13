from strategies.post_earnings_drift import PostEarningsDriftStrategy
from backtesting.backtester import Backtester
from analytics.metrics import total_return, sharpe_ratio
from optimizer import optimize_pead_strategy


def screen_pead_tickers(stock_data, all_earnings, initial_cash, min_alpha=0.0, min_sharpe=0.3, top_n=None):
    """
    Runs PEAD optimizer on every ticker and returns two lists:
      qualified - tickers where strategy beats B&H, sorted by alpha descending
      all_results - every ticker's result for the full ranking table
    """
    all_results = []

    for ticker, data in stock_data.items():
        earnings_events = all_earnings.get(ticker)
        if earnings_events is None or earnings_events.empty:
            all_results.append({'ticker': ticker, 'skip': True})
            continue

        best = optimize_pead_strategy(data, earnings_events, initial_cash)
        if best is None:
            all_results.append({'ticker': ticker, 'skip': True})
            continue

        strategy = PostEarningsDriftStrategy(
            earnings_events, best['surprise_threshold'], best['hold_days']
        )
        signals = strategy.generate_signals(data)
        results, _ = Backtester(initial_cash).run(signals)

        strat_ret  = total_return(results['portfolio_value'])
        bench_ret  = total_return(results['benchmark_value'])
        alpha      = strat_ret - bench_ret
        sharpe     = sharpe_ratio(results['daily_return'])

        all_results.append({
            'ticker':       ticker,
            'skip':         False,
            'strat_return': strat_ret,
            'bench_return': bench_ret,
            'alpha':        alpha,
            'sharpe':       sharpe,
            'threshold':    best['surprise_threshold'],
            'hold_days':    best['hold_days'],
        })

    all_results = [r for r in all_results if not r.get('skip')]
    all_results.sort(key=lambda x: x['alpha'], reverse=True)

    qualified = [r for r in all_results if r['alpha'] >= min_alpha and r['sharpe'] >= min_sharpe]
    if top_n is not None:
        qualified = qualified[:top_n]

    return qualified, all_results


def print_screening_results(qualified, all_results):
    header = f"  {'Ticker':<8} {'Strategy':>10} {'B&H':>10} {'Alpha':>10} {'Sharpe':>8} {'Threshold':>10} {'Hold':>6}"
    divider = '  ' + '-' * (len(header) - 2)

    print('\n=== PEAD Screener Results ===')
    print(f'\nQUALIFIED ({len(qualified)} tickers with positive alpha and Sharpe > 0.3):')
    print(header)
    print(divider)
    for r in qualified:
        print(f"  {r['ticker']:<8} {r['strat_return']:>10.2%} {r['bench_return']:>10.2%} "
              f"{r['alpha']:>+10.2%} {r['sharpe']:>8.2f} {r['threshold']:>10.2f} {r['hold_days']:>6}")

    not_qualified = [r for r in all_results if r not in qualified]
    if not_qualified:
        print(f'\nNOT QUALIFIED ({len(not_qualified)} tickers):')
        print(header)
        print(divider)
        for r in not_qualified:
            print(f"  {r['ticker']:<8} {r['strat_return']:>10.2%} {r['bench_return']:>10.2%} "
                  f"{r['alpha']:>+10.2%} {r['sharpe']:>8.2f} {r['threshold']:>10.2f} {r['hold_days']:>6}")
