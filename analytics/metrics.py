import numpy as np


def total_return(portfolio_values):
    return (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1


def annualized_return(portfolio_values):
    total = total_return(portfolio_values)
    n_days = len(portfolio_values)
    return (1 + total) ** (252 / n_days) - 1


def sharpe_ratio(daily_returns, risk_free_rate=0):
    excess = daily_returns.dropna() - (risk_free_rate / 252)
    if excess.std() == 0:
        return 0
    return (excess.mean() / excess.std()) * np.sqrt(252)


def sortino_ratio(daily_returns, risk_free_rate=0):
    excess = daily_returns.dropna() - (risk_free_rate / 252)
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float('inf') if excess.mean() > 0 else 0
    return (excess.mean() / downside.std()) * np.sqrt(252)


def annualized_volatility(daily_returns):
    return daily_returns.dropna().std() * np.sqrt(252)


def calmar_ratio(portfolio_values):
    ann = annualized_return(portfolio_values)
    dd = abs(max_drawdown(portfolio_values))
    if dd == 0:
        return float('inf')
    return ann / dd


def max_drawdown(portfolio_values):
    running_max = portfolio_values.cummax()
    drawdown = (portfolio_values - running_max) / running_max
    return drawdown.min()


def trade_stats(trades):
    if not trades:
        return {}

    pnls = [t['pnl'] for t in trades]
    winners = [p for p in pnls if p > 0]
    losers = [p for p in pnls if p < 0]

    gross_profit = sum(winners) if winners else 0
    gross_loss = abs(sum(losers)) if losers else 0

    return {
        'num_trades': len(trades),
        'win_rate': len(winners) / len(trades),
        'profit_factor': gross_profit / gross_loss if gross_loss > 0 else float('inf'),
        'avg_trade_pnl': np.mean(pnls),
        'best_trade': max(pnls),
        'worst_trade': min(pnls),
    }


def print_metrics(results, trades=None):
    pv = results['portfolio_value']
    bv = results['benchmark_value']
    dr = results['daily_return']

    strat_return   = total_return(pv)
    bench_return   = total_return(bv)
    ann_return     = annualized_return(pv)
    sharpe         = sharpe_ratio(dr)
    sortino        = sortino_ratio(dr)
    calmar         = calmar_ratio(pv)
    ann_vol        = annualized_volatility(dr)
    drawdown       = max_drawdown(pv)
    alpha          = strat_return - bench_return

    print(f"  Total Return:       {strat_return:>10.2%}   (benchmark: {bench_return:.2%}, alpha: {alpha:+.2%})")
    print(f"  Annualized Return:  {ann_return:>10.2%}")
    print(f"  Annualized Vol:     {ann_vol:>10.2%}")
    print(f"  Sharpe Ratio:       {sharpe:>10.2f}")
    print(f"  Sortino Ratio:      {sortino:>10.2f}" if sortino != float('inf') else f"  Sortino Ratio:           ∞")
    print(f"  Calmar Ratio:       {calmar:>10.2f}" if calmar != float('inf') else f"  Calmar Ratio:            ∞")
    print(f"  Max Drawdown:       {drawdown:>10.2%}")

    if trades is not None:
        stats = trade_stats(trades)
        if stats:
            print(f"  Trades:             {stats['num_trades']:>10}")
            print(f"  Win Rate:           {stats['win_rate']:>10.2%}")
            pf = stats['profit_factor']
            print(f"  Profit Factor:      {pf:>10.2f}" if pf != float('inf') else f"  Profit Factor:         ∞ (no losses)")
            print(f"  Avg Trade P&L:      ${stats['avg_trade_pnl']:>9.2f}")
            print(f"  Best Trade:         ${stats['best_trade']:>9.2f}")
            print(f"  Worst Trade:        ${stats['worst_trade']:>9.2f}")
        else:
            print("  No completed trades.")
