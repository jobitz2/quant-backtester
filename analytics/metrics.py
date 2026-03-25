import numpy as np


def total_return(portfolio_values):
    start_value = portfolio_values.iloc[0]
    end_value = portfolio_values.iloc[-1]
    return (end_value / start_value) - 1


def sharpe_ratio(daily_returns, risk_free_rate=0):
    excess_returns = daily_returns.dropna() - (risk_free_rate / 252)

    if excess_returns.std() == 0:
        return 0

    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)


def max_drawdown(portfolio_values):
    running_max = portfolio_values.cummax()
    drawdown = (portfolio_values - running_max) / running_max
    return drawdown.min()


def print_metrics(results):
    portfolio_values = results['portfolio_value']
    daily_returns = results['daily_return']

    strategy_total_return = total_return(portfolio_values)
    strategy_sharpe = sharpe_ratio(daily_returns)
    strategy_max_drawdown = max_drawdown(portfolio_values)

    print('\nStrategy Performance')
    print(f'Total Return: {strategy_total_return:.2%}')
    print(f'Sharpe Ratio: {strategy_sharpe:.2f}')
    print(f'Max Drawdown: {strategy_max_drawdown:.2%}')