import numpy as np
from strategies.base_strategy import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        signals = data.copy()
        
        signals['short_ma'] = \
            signals['Close'].ewm(span=self.short_window, adjust=False).mean()

        signals['long_ma'] = \
            signals['Close'].ewm(span=self.long_window, adjust=False).mean()

        signals['signal'] = 0

        signals.loc[signals['short_ma'] > signals['long_ma'], 'signal'] = 1
        signals.loc[signals['short_ma'] < signals['long_ma'], 'signal'] = -1

        signals['position_change'] = signals['signal'].diff()

        return signals