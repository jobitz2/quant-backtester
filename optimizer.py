from strategies.momentum import MomentumStrategy
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

                    strategy = MomentumStrategy(
                        window,
                        buy_threshold,
                        sell_threshold,
                        trend_window
                    )

                    signals = strategy.generate_signals(data)

                    backtester = Backtester(initial_cash)
                    results = backtester.run(signals)

                    strategy_return = total_return(results['portfolio_value'])
                    strategy_sharpe = sharpe_ratio(results['daily_return'])
                    strategy_drawdown = max_drawdown(results['portfolio_value'])

                    if best_result is None or strategy_sharpe > best_result:
                        best_result = strategy_sharpe
                        best_settings = {
                            'window': window,
                            'buy_threshold': buy_threshold,
                            'sell_threshold': sell_threshold,
                            'trend_window': trend_window,
                            'total_return': strategy_return,
                            'sharpe_ratio': strategy_sharpe,
                            'max_drawdown': strategy_drawdown
                        }

    return best_settings