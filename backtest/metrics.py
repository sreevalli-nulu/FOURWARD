import numpy as np, pandas as pd

def metrics(equity, net_returns, periods_per_year=365):
    yrs = len(equity) / periods_per_year
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / yrs) - 1
    dd = equity / equity.cummax() - 1
    vol = net_returns.std() * np.sqrt(periods_per_year)
    downside = net_returns[net_returns < 0].std() * np.sqrt(periods_per_year)
    return {
        "CAGR": cagr, "Max drawdown": dd.min(), "Volatility": vol,
        "Sharpe": (net_returns.mean() * periods_per_year) / vol if vol else np.nan,
        "Sortino": (net_returns.mean() * periods_per_year) / downside if downside else np.nan,
        "Calmar": cagr / abs(dd.min()) if dd.min() else np.nan,
        "Exposure": float((net_returns != 0).mean()),
        "Longest DD (days)": int((dd < 0).astype(int).groupby((dd == 0).cumsum()).cumsum().max()),
        "Final equity": float(equity.iloc[-1]),
    }