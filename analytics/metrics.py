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
    benchmark_values = results['benchmark_value']
    daily_returns = results['daily_return']

    strategy_return = total_return(portfolio_values)
    benchmark_return = total_return(benchmark_values)

    print('\nStrategy vs Benchmark')
    print(f'Strategy Return: {strategy_return:.2%}')
    print(f'Benchmark Return: {benchmark_return:.2%}')