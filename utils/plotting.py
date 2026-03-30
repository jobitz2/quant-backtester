import matplotlib.pyplot as plt


def ma_plot_price_and_signals(results, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(results.index, results['Close'], label='Close Price')
    plt.plot(results.index, results['short_ma'], label='Short MA')
    plt.plot(results.index, results['long_ma'], label='Long MA')

    buy_signals = results[results['position_change'] == 2]
    sell_signals = results[results['position_change'] == -2]

    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', label='Buy')
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', label='Sell')

    plt.title(f'{ticker} Price and Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def mm_plot_price_and_signals(results, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(results.index, results['Close'], label='Close Price')

    if 'short_ma' in results.columns:
        plt.plot(results.index, results['short_ma'], label='Short MA')

    if 'long_ma' in results.columns:
        plt.plot(results.index, results['long_ma'], label='Long MA')

    if 'moving_average' in results.columns:
        plt.plot(results.index, results['moving_average'], label='Moving Average')

    buy_signals = results[results['position_change'] == 1]
    sell_signals = results[results['position_change'] == -1]

    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', label='Buy')
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', label='Sell')

    plt.title(f'{ticker} Price and Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_portfolio(results, ticker):
    plt.figure(figsize=(12, 6))

    plt.plot(results.index, results['portfolio_value'], label='Strategy')
    plt.plot(results.index, results['benchmark_value'], label='Buy & Hold')

    plt.title(f'{ticker} Strategy vs Buy & Hold')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(True)
    plt.show()

