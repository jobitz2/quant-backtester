import pandas as pd
import yfinance as yf

from config import TICKERS


def fetch_earnings_for_ticker(ticker):
    stock = yf.Ticker(ticker)
    earnings = stock.earnings_dates

    if earnings is None or earnings.empty:
        return pd.DataFrame(columns=['ticker', 'date', 'surprise'])

    earnings = earnings.reset_index()

    earnings = earnings[['Earnings Date', 'Surprise(%)']].copy()
    earnings.rename(columns={
        'Earnings Date': 'date',
        'Surprise(%)': 'surprise'
    }, inplace=True)

    earnings['ticker'] = ticker
    earnings['surprise'] = earnings['surprise'] / 100

    earnings = earnings[['ticker', 'date', 'surprise']]
    earnings.dropna(subset=['date', 'surprise'], inplace=True)

    return earnings


def build_earnings_csv(output_file):
    all_earnings = []

    for ticker in TICKERS:
        try:
            ticker_earnings = fetch_earnings_for_ticker(ticker)

            if not ticker_earnings.empty:
                all_earnings.append(ticker_earnings)

            print(f'Finished {ticker}')

        except Exception as error:
            print(f'Could not fetch earnings for {ticker}: {error}')

    if all_earnings:
        final_df = pd.concat(all_earnings, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=['ticker', 'date', 'surprise'])

    final_df.to_csv(output_file, index=False)
    print(f'Saved earnings data to {output_file}')


if __name__ == '__main__':
    build_earnings_csv('data/earnings_events.csv')