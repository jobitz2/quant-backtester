import os
import robin_stocks.robinhood as rh


def login():
    username = os.environ.get('ROBINHOOD_USERNAME')
    password = os.environ.get('ROBINHOOD_PASSWORD')
    if not username or not password:
        raise EnvironmentError(
            "Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD environment variables before trading live."
        )
    rh.login(username, password)


def get_buying_power():
    profile = rh.profiles.load_account_profile()
    return float(profile['buying_power'])


def get_robinhood_positions():
    """Returns {ticker: shares} for all open Robinhood positions."""
    positions = rh.account.get_open_stock_positions()
    result = {}
    for pos in positions:
        instrument = rh.stocks.get_stock_by_url(pos['instrument'])
        ticker = instrument['symbol']
        result[ticker] = float(pos['quantity'])
    return result


def get_current_price(ticker):
    quotes = rh.stocks.get_latest_price(ticker)
    if quotes and quotes[0] is not None:
        return float(quotes[0])
    return None


def place_buy(ticker, dollars, dry_run=True):
    if dry_run:
        print(f"  [DRY RUN] BUY ${dollars:.2f} of {ticker}")
        return None
    order = rh.orders.order_buy_fractional_by_price(ticker, dollars, timeInForce='gfd')
    print(f"  [LIVE] BUY order placed for ${dollars:.2f} of {ticker} — id: {order.get('id')}")
    return order


def place_sell(ticker, shares, dry_run=True):
    if dry_run:
        print(f"  [DRY RUN] SELL {shares:.4f} shares of {ticker}")
        return None
    order = rh.orders.order_sell_fractional_by_quantity(ticker, shares, timeInForce='gfd')
    print(f"  [LIVE] SELL order placed for {shares:.4f} shares of {ticker} — id: {order.get('id')}")
    return order
