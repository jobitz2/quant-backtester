from strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    def __init__(self, window, buy_threshold, sell_threshold, trend_window):
        self.window = window
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.trend_window = trend_window

    def generate_signals(self, data):
        signals = data.copy()

        # momentum = % change over window
        signals['momentum'] = signals['Close'].pct_change(periods=self.window)

        # trend filter (long-term moving average)
        signals['trend_ma'] = signals['Close'].rolling(window=self.trend_window).mean()

        signals['signal'] = 0

        buy_condition = \
            (signals['momentum'] > self.buy_threshold) & \
            (signals['Close'] > signals['trend_ma'])

        sell_condition = \
            (signals['momentum'] < self.sell_threshold) | \
            (signals['Close'] < signals['trend_ma'])

        signals.loc[buy_condition, 'signal'] = 1
        signals.loc[sell_condition, 'signal'] = -1

        signals['position_change'] = signals['signal'].diff()

        return signals