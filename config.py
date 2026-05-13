DRY_RUN = True   # Set False only when ready to place real Robinhood orders

TICKERS = [
    # Financials
    'JPM', 'GS', 'BAC', 'C', 'WFC', 'MS', 'BLK', 'AXP', 'USB', 'COF', 'SCHW', 'PNC', 'TFC',
    # Healthcare
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'ABT', 'TMO', 'BMY', 'AMGN', 'GILD', 'CVS', 'HUM',
    # Consumer staples
    'KO', 'PG', 'WMT', 'COST', 'PEP', 'MO', 'PM', 'CL', 'GIS', 'HSY',
    # Consumer discretionary
    'MCD', 'NKE', 'SBUX', 'TGT', 'HD', 'LOW', 'TJX', 'MAR', 'YUM', 'DRI',
    # Industrials
    'CAT', 'HON', 'GE', 'UPS', 'FDX', 'DE', 'EMR', 'ETN', 'ITW', 'RTX',
    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC',
    # Technology (value)
    'IBM', 'INTC', 'CSCO', 'ORCL', 'TXN', 'QCOM',
    # Materials
    'LIN', 'APD', 'NEM', 'FCX',
]

SCREENER_TOP_N   = 10    # number of tickers to trade after screening
STOP_LOSS_PCT    = None  # set to e.g. 0.10 to exit if position drops 10% from entry
USE_REGIME_FILTER = False  # set True to block entries when SPY < 200-day MA
REGIME_MA_DAYS   = 200   # SPY MA window (only used when USE_REGIME_FILTER=True)

START_DATE = '2020-01-01'
END_DATE = '2025-01-01'

INITIAL_CASH = 2000
COMMISSION = 0.001   # 0.1% per trade
SLIPPAGE   = 0.001   # 0.1% per trade

EARNINGS_SURPRISE_THRESHOLD = 0.05
PEAD_HOLD_DAYS = 20
EARNINGS_FILE = 'data/earnings_events.csv'

SHORT_WINDOW = 10
LONG_WINDOW = 100

MOMENTUM_WINDOW = 20
MOMENTUM_BUY_THRESHOLD = 0.08
MOMENTUM_SELL_THRESHOLD = -0.05
MOMENTUM_TREND_WINDOW = 100