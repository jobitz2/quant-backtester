from strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    def __init__(self, window, buy_threshold, sell_threshold):
        self.window = window
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signals(self, data):
        signals = data.copy()

        signals['momentum'] = signals['Close'].pct_change(periods=self.window)

        signals['signal'] = 0
        signals.loc[signals['momentum'] > self.buy_threshold, 'signal'] = 1
        signals.loc[signals['momentum'] < self.sell_threshold, 'signal'] = -1

        signals['position_change'] = signals['signal'].diff()

        return signals