import pandas as pd

from strategies.base_strategy import BaseStrategy


class PostEarningsDriftStrategy(BaseStrategy):
    def __init__(self, earnings_events, surprise_threshold, hold_days,
                 long_only=True, regime_data=None, regime_ma_days=200):
        self.earnings_events   = earnings_events
        self.surprise_threshold = surprise_threshold
        self.hold_days         = hold_days
        self.long_only         = long_only
        self.regime_data       = regime_data    # SPY Close series, index-aligned
        self.regime_ma_days    = regime_ma_days

    def generate_signals(self, data):
        signals = data.copy()
        signal_values = pd.Series(0, index=signals.index, dtype=int)

        # Precompute regime MA so we can check it per event date
        if self.regime_data is not None:
            regime_ma = self.regime_data.rolling(self.regime_ma_days).mean()
        else:
            regime_ma = None

        for _, event in self.earnings_events.iterrows():
            event_date = event['date']
            surprise   = event['surprise']

            valid_dates = signals.index[signals.index >= event_date]
            if len(valid_dates) == 0:
                continue

            start_date = valid_dates[0]
            start_loc  = signals.index.get_loc(start_date)
            end_loc    = min(start_loc + self.hold_days, len(signals.index))

            # Regime filter: skip long entries when SPY is below its MA
            if regime_ma is not None and start_date in regime_ma.index:
                spy_price = self.regime_data.get(start_date)
                spy_ma    = regime_ma.get(start_date)
                if spy_price is not None and spy_ma is not None and spy_price < spy_ma:
                    continue  # bear market — skip this signal

            if surprise >= self.surprise_threshold:
                signal_values.iloc[start_loc:end_loc] = 1
                if end_loc < len(signals.index):
                    signal_values.iloc[end_loc] = -1

            elif surprise <= -self.surprise_threshold and not self.long_only:
                signal_values.iloc[start_loc:end_loc] = -1
                if end_loc < len(signals.index):
                    signal_values.iloc[end_loc] = 1

        signals['signal'] = signal_values
        signals['position_change'] = signals['signal'].diff()

        return signals
