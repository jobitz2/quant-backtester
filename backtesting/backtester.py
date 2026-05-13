class Backtester:
    def __init__(self, initial_cash, commission=0.001, slippage=0.001, long_only=True, stop_loss_pct=None):
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.long_only = long_only
        self.stop_loss_pct = stop_loss_pct  # e.g. 0.07 exits if price falls 7% below entry

    def run(self, signals):
        results = signals.copy()

        cash = self.initial_cash
        position = 0.0
        portfolio_values = []
        trades = []
        entry_price = None
        entry_date = None

        for index, row in results.iterrows():
            price = float(row['Close'])
            signal = int(row['signal'])

            # Stop loss check — override signal if long and price fell too far
            if (self.stop_loss_pct is not None
                    and position > 0
                    and entry_price is not None
                    and price <= entry_price * (1 - self.stop_loss_pct)):
                signal = -1  # force exit

            if signal == 1 and position == 0:
                buy_price = price * (1 + self.slippage)
                shares = (cash / buy_price) * (1 - self.commission)
                cash = 0.0
                position = shares
                entry_price = buy_price
                entry_date = index

            elif signal == 1 and position < 0:
                buy_price = price * (1 + self.slippage)
                cost = abs(position) * buy_price * (1 + self.commission)
                cash -= cost
                trades.append(_make_trade(entry_date, index, 'short', entry_price, buy_price, abs(position)))
                position = 0.0

                shares = (cash / buy_price) * (1 - self.commission)
                cash = 0.0
                position = shares
                entry_price = buy_price
                entry_date = index

            elif signal == -1 and position > 0:
                sell_price = price * (1 - self.slippage)
                proceeds = position * sell_price * (1 - self.commission)
                trades.append(_make_trade(entry_date, index, 'long', entry_price, sell_price, position))
                cash = proceeds
                position = 0.0
                entry_price = None
                entry_date = None

            elif signal == -1 and position == 0 and not self.long_only:
                sell_price = price * (1 - self.slippage)
                shares_to_short = cash / sell_price
                cash += shares_to_short * sell_price * (1 - self.commission)
                position = -shares_to_short
                entry_price = sell_price
                entry_date = index

            portfolio_value = cash + position * price
            portfolio_values.append(portfolio_value)

        if position != 0:
            last_price = float(results['Close'].iloc[-1])
            last_date = results.index[-1]
            if position > 0:
                sell_price = last_price * (1 - self.slippage)
                proceeds = position * sell_price * (1 - self.commission)
                trades.append(_make_trade(entry_date, last_date, 'long', entry_price, sell_price, position))
            else:
                buy_price = last_price * (1 + self.slippage)
                cost = abs(position) * buy_price * (1 + self.commission)
                trades.append(_make_trade(entry_date, last_date, 'short', entry_price, buy_price, abs(position)))

        results['portfolio_value'] = portfolio_values
        results['daily_return'] = results['portfolio_value'].pct_change()

        first_price = results['Close'].iloc[0]
        results['benchmark_value'] = (self.initial_cash / first_price) * results['Close']

        return results, trades


def _make_trade(entry_date, exit_date, direction, entry_price, exit_price, shares):
    if direction == 'long':
        pnl = (exit_price - entry_price) * shares
    else:
        pnl = (entry_price - exit_price) * shares
    pnl_pct = pnl / (entry_price * shares) if entry_price and shares else 0
    return {
        'entry_date':  entry_date,
        'exit_date':   exit_date,
        'direction':   direction,
        'entry_price': round(entry_price, 4),
        'exit_price':  round(exit_price, 4),
        'shares':      round(shares, 4),
        'pnl':         round(pnl, 2),
        'pnl_pct':     round(pnl_pct, 4),
    }
