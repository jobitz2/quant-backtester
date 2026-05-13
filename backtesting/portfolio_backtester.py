import pandas as pd


class PortfolioBacktester:
    """
    Single-pool capital allocation across multiple tickers.
    Exits are processed before entries on the same day.
    Position sizes are scaled by earnings surprise magnitude when surprise
    data is available; otherwise falls back to equal weighting.
    Stop loss exits any long position that drops stop_loss_pct from entry.
    """

    def __init__(self, initial_cash, commission=0.001, slippage=0.001, stop_loss_pct=None):
        self.initial_cash  = initial_cash
        self.commission    = commission
        self.slippage      = slippage
        self.stop_loss_pct = stop_loss_pct

    def run(self, all_signals, surprise_map=None):
        """
        all_signals  : dict  ticker -> signals DataFrame
        surprise_map : dict  ticker -> surprise fraction (optional, enables scaled sizing)
        """
        common_dates = sorted(
            set.intersection(*[set(df.index) for df in all_signals.values()])
        )

        cash = self.initial_cash
        positions = {}   # ticker -> {shares, entry_price, entry_date}
        trades = []
        portfolio_values = []

        for date in common_dates:
            # --- Stop-loss check before processing signals ---
            for ticker, pos in list(positions.items()):
                if self.stop_loss_pct is None:
                    break
                if date not in all_signals[ticker].index:
                    continue
                price = float(all_signals[ticker].loc[date, 'Close'])
                if price <= pos['entry_price'] * (1 - self.stop_loss_pct):
                    sell_price = price * (1 - self.slippage)
                    proceeds = pos['shares'] * sell_price * (1 - self.commission)
                    pnl = (sell_price - pos['entry_price']) * pos['shares']
                    trades.append(_make_trade(ticker, pos['entry_date'], date, pos['entry_price'], sell_price, pos['shares'], pnl))
                    cash += proceeds
                    del positions[ticker]

            # --- Exits (signal = -1) ---
            for ticker, signals_df in all_signals.items():
                if date not in signals_df.index or ticker not in positions:
                    continue
                if int(signals_df.loc[date, 'signal']) == -1:
                    price = float(signals_df.loc[date, 'Close'])
                    sell_price = price * (1 - self.slippage)
                    pos = positions[ticker]
                    proceeds = pos['shares'] * sell_price * (1 - self.commission)
                    pnl = (sell_price - pos['entry_price']) * pos['shares']
                    trades.append(_make_trade(ticker, pos['entry_date'], date, pos['entry_price'], sell_price, pos['shares'], pnl))
                    cash += proceeds
                    del positions[ticker]

            # --- Entries (signal = 1) ---
            new_entries = [
                ticker for ticker, signals_df in all_signals.items()
                if date in signals_df.index
                and int(signals_df.loc[date, 'signal']) == 1
                and ticker not in positions
            ]

            if new_entries and cash > 1.0:
                allocs = _scale_allocations(cash, new_entries, surprise_map)
                for ticker, alloc in allocs.items():
                    price = float(all_signals[ticker].loc[date, 'Close'])
                    buy_price = price * (1 + self.slippage)
                    shares = (alloc / buy_price) * (1 - self.commission)
                    cash -= alloc
                    positions[ticker] = {
                        'shares':      shares,
                        'entry_price': buy_price,
                        'entry_date':  date,
                    }

            portfolio_value = cash + sum(
                positions[t]['shares'] * float(all_signals[t].loc[date, 'Close'])
                for t in positions if date in all_signals[t].index
            )
            portfolio_values.append(portfolio_value)

        # Close remaining positions at end
        last_date = common_dates[-1]
        for ticker, pos in list(positions.items()):
            if last_date in all_signals[ticker].index:
                price = float(all_signals[ticker].loc[last_date, 'Close'])
                sell_price = price * (1 - self.slippage)
                pnl = (sell_price - pos['entry_price']) * pos['shares']
                trades.append(_make_trade(ticker, pos['entry_date'], last_date, pos['entry_price'], sell_price, pos['shares'], pnl))

        result = pd.DataFrame({'portfolio_value': portfolio_values}, index=common_dates)
        result['daily_return'] = result['portfolio_value'].pct_change()

        alloc_per_ticker = self.initial_cash / len(all_signals)
        benchmark = pd.Series(0.0, index=common_dates)
        for ticker, signals_df in all_signals.items():
            aligned = signals_df['Close'].reindex(common_dates)
            benchmark += (alloc_per_ticker / aligned.iloc[0]) * aligned
        result['benchmark_value'] = benchmark.values

        return result, trades


def _scale_allocations(available_cash, tickers, surprise_map):
    """
    Returns {ticker: dollar_alloc} scaled by surprise magnitude.
    Falls back to equal weighting when surprise_map is None or incomplete.
    """
    if not surprise_map:
        equal = available_cash / len(tickers)
        return {t: equal for t in tickers}

    weights = {}
    for t in tickers:
        surprise = surprise_map.get(t)
        weights[t] = abs(surprise) if surprise is not None else 0.0

    total_weight = sum(weights.values())
    if total_weight == 0:
        equal = available_cash / len(tickers)
        return {t: equal for t in tickers}

    return {t: available_cash * (weights[t] / total_weight) for t in tickers}


def _make_trade(ticker, entry_date, exit_date, entry_price, exit_price, shares, pnl):
    pnl_pct = pnl / (entry_price * shares) if entry_price and shares else 0
    return {
        'ticker':      ticker,
        'entry_date':  entry_date,
        'exit_date':   exit_date,
        'entry_price': round(entry_price, 4),
        'exit_price':  round(exit_price, 4),
        'shares':      round(shares, 4),
        'pnl':         round(pnl, 2),
        'pnl_pct':     round(pnl_pct, 4),
    }
