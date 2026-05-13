import pandas as pd


def load_earnings_events(filepath, ticker):
    earnings = pd.read_csv(filepath)

    required_columns = {'ticker', 'date', 'surprise'}
    if not required_columns.issubset(earnings.columns):
        raise ValueError(
            "Earnings file must contain columns: 'ticker', 'date', 'surprise'"
        )

    earnings = earnings[earnings['ticker'] == ticker].copy()
    earnings['date'] = pd.to_datetime(earnings['date'], utc=True).dt.tz_localize(None)
    earnings.sort_values('date', inplace=True)

    return earnings