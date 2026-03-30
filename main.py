# from config import TICKERS, START_DATE, END_DATE, INITIAL_CASH, SHORT_WINDOW, LONG_WINDOW
# from data.downloader import download_multiple_stocks
# from strategies.moving_average import MovingAverageCrossoverStrategy
# from backtesting.backtester import Backtester
# from analytics.metrics import print_metrics
# from utils.plotting import plot_price_and_signals, plot_portfolio


# def main():
#     stock_data = download_multiple_stocks(TICKERS, START_DATE, END_DATE)
#     for ticker in stock_data:
#         data = stock_data[ticker]

#         strategy = MovingAverageCrossoverStrategy(SHORT_WINDOW, LONG_WINDOW)
#         signals = strategy.generate_signals(data)

#         backtester = Backtester(INITIAL_CASH)
#         results = backtester.run(signals)

#         print_metrics(results)
#         ma_plot_price_and_signals(results, ticker)
#         plot_portfolio(results, ticker)
#         print_metrics(results)


# if __name__ == '__main__':
#     main()
from config import \
    TICKERS, START_DATE, END_DATE, INITIAL_CASH, \
    MOMENTUM_WINDOW, MOMENTUM_BUY_THRESHOLD, MOMENTUM_SELL_THRESHOLD,\
    MOMENTUM_TREND_WINDOW
from data.downloader import download_multiple_stocks
from strategies.momentum import MomentumStrategy
from backtesting.backtester import Backtester
from analytics.metrics import print_metrics
from utils.plotting import ma_plot_price_and_signals, mm_plot_price_and_signals, plot_portfolio
from optimizer import optimize_momentum_strategy


def main():
    stock_data = download_multiple_stocks(TICKERS, START_DATE, END_DATE)

    for ticker in stock_data:
        data = stock_data[ticker]

        best = optimize_momentum_strategy(data, INITIAL_CASH)

        strategy = MomentumStrategy(
            best['window'],
            best['buy_threshold'],
            best['sell_threshold'],
            best['trend_window']
        )
        
        signals = strategy.generate_signals(data)

        backtester = Backtester(INITIAL_CASH)
        results = backtester.run(signals)

        print_metrics(results)
        mm_plot_price_and_signals(results, ticker) #plots momentum method
        plot_portfolio(results, ticker)
        print_metrics(results)


if __name__ == '__main__':
    main()