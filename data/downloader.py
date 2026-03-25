import yfinance as yf
import pandas as pd


def download_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f'No data found for {ticker}')

    if hasattr(data.columns, 'nlevels') and data.columns.nlevels > 1:
        data.columns = data.columns.get_level_values(0)

    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    data.dropna(inplace=True)

    return data


def download_multiple_stocks(tickers, start_date, end_date):
    stock_data = {}

    for ticker in tickers:
        try:
            stock_data[ticker] = download_stock_data(ticker, start_date, end_date)
        except ValueError as error:
            print(error)

    return stock_data