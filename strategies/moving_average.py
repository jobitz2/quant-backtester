import numpy as np
from strategies.base_strategy import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        signals = data.copy()

        signals['short_ma'] = signals['Close'].rolling(window=self.short_window).mean()
        signals['long_ma'] = signals['Close'].rolling(window=self.long_window).mean()

        signals['signal'] = 0

        signals.loc[signals['short_ma'] > signals['long_ma'], 'signal'] = 1
        signals.loc[signals['short_ma'] < signals['long_ma'], 'signal'] = -1

        signals['position_change'] = signals['signal'].diff()

        return signals