from strategies.momentum import MomentumStrategy
from strategies.post_earnings_drift import PostEarningsDriftStrategy
from backtesting.backtester import Backtester
from analytics.metrics import total_return, sharpe_ratio, max_drawdown


def optimize_momentum_strategy(data, initial_cash):
    windows = [10, 20, 30, 60]
    buy_thresholds = [0.03, 0.05, 0.08, 0.10]
    sell_thresholds = [-0.03, -0.05, -0.08]
    trend_windows = [50, 100, 200]

    best_result = None
    best_settings = None

    for window in windows:
        for buy_threshold in buy_thresholds:
            for sell_threshold in sell_thresholds:
                for trend_window in trend_windows:
                    strategy = MomentumStrategy(window, buy_threshold, sell_threshold, trend_window)
                    signals = strategy.generate_signals(data)
                    backtester = Backtester(initial_cash)
                    results, _ = backtester.run(signals)

                    strat_sharpe   = sharpe_ratio(results['daily_return'])
                    strat_return   = total_return(results['portfolio_value'])
                    strat_drawdown = max_drawdown(results['portfolio_value'])

                    if best_result is None or strat_sharpe > best_result:
                        best_result = strat_sharpe
                        best_settings = {
                            'window': window,
                            'buy_threshold': buy_threshold,
                            'sell_threshold': sell_threshold,
                            'trend_window': trend_window,
                            'total_return': strat_return,
                            'sharpe_ratio': strat_sharpe,
                            'max_drawdown': strat_drawdown,
                        }

    return best_settings


def optimize_pead_strategy(data, earnings_events, initial_cash, stop_loss_pct=None):
    surprise_thresholds = [0.02, 0.05, 0.08, 0.10, 0.15]
    hold_days_options   = [5, 10, 20, 30, 60]

    best_sharpe  = None
    best_settings = None

    for threshold in surprise_thresholds:
        for hold_days in hold_days_options:
            strategy = PostEarningsDriftStrategy(earnings_events, threshold, hold_days)
            signals  = strategy.generate_signals(data)

            backtester = Backtester(initial_cash, stop_loss_pct=stop_loss_pct)
            results, _ = backtester.run(signals)

            strat_sharpe   = sharpe_ratio(results['daily_return'])
            strat_return   = total_return(results['portfolio_value'])
            strat_drawdown = max_drawdown(results['portfolio_value'])

            if best_sharpe is None or strat_sharpe > best_sharpe:
                best_sharpe = strat_sharpe
                best_settings = {
                    'surprise_threshold': threshold,
                    'hold_days':          hold_days,
                    'total_return':       strat_return,
                    'sharpe_ratio':       strat_sharpe,
                    'max_drawdown':       strat_drawdown,
                }

    return best_settings


def walk_forward_pead(data, earnings_events, initial_cash,
                      train_pct=0.6, stop_loss_pct=None):
    """
    Optimizes PEAD params on the first train_pct of the price history,
    then evaluates on the remaining out-of-sample period.
    Returns best params and their out-of-sample performance.
    """
    split = int(len(data) * train_pct)
    train_data = data.iloc[:split]
    test_data  = data.iloc[split:]

    cutoff_date = train_data.index[-1]
    train_earnings = earnings_events[earnings_events['date'] <= cutoff_date]
    test_earnings  = earnings_events[earnings_events['date'] >  cutoff_date]

    if train_earnings.empty or test_earnings.empty:
        return None

    best = optimize_pead_strategy(train_data, train_earnings, initial_cash, stop_loss_pct)
    if best is None:
        return None

    # Evaluate best params on out-of-sample data
    strategy   = PostEarningsDriftStrategy(test_earnings, best['surprise_threshold'], best['hold_days'])
    signals    = strategy.generate_signals(test_data)
    backtester = Backtester(initial_cash, stop_loss_pct=stop_loss_pct)
    results, trades = backtester.run(signals)

    oos_sharpe   = sharpe_ratio(results['daily_return'])
    oos_return   = total_return(results['portfolio_value'])
    oos_drawdown = max_drawdown(results['portfolio_value'])
    bench_return = total_return(results['benchmark_value'])

    return {
        'surprise_threshold':  best['surprise_threshold'],
        'hold_days':           best['hold_days'],
        'train_sharpe':        best['sharpe_ratio'],
        'oos_sharpe':          oos_sharpe,
        'oos_return':          oos_return,
        'oos_drawdown':        oos_drawdown,
        'oos_alpha':           oos_return - bench_return,
        'train_end':           str(cutoff_date.date()),
        'test_start':          str(test_data.index[0].date()),
    }
