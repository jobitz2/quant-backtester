class Backtester:
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash

    def run(self, signals):
        results = signals.copy()

        cash = self.initial_cash
        shares = 0
        portfolio_values = []

        for index, row in results.iterrows():
            price = float(row['Close'])
            signal = int(row['signal'])

            # BUY
            if signal == 1 and shares == 0:
                shares = cash / price
                cash = 0

            # SELL
            elif signal == -1 and shares > 0:
                cash = shares * price
                shares = 0

            portfolio_value = cash + (shares * price)
            portfolio_values.append(portfolio_value)

        results['portfolio_value'] = portfolio_values
        results['daily_return'] = results['portfolio_value'].pct_change()

        # Buy and hold benchmark
        first_price = results['Close'].iloc[0]
        shares_benchmark = self.initial_cash / first_price

        results['benchmark_value'] = shares_benchmark * results['Close']

        return results