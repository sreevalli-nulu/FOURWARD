import numpy as np, pandas as pd

def run_backtest(df, position, fee=0.001, slippage=0.0005, capital=10_000):
    """position: 0/1 Series decided on close of bar t; executed at open of t+1."""
    pos_exec = position.shift(1).fillna(0)          # executed at open of next bar
    ret = df["open"].pct_change().fillna(0)         # open(t-1) -> open(t)
    strat_ret = pos_exec.shift(1).fillna(0) * ret    # position held over that interval
    turnover = pos_exec.diff().abs().fillna(pos_exec)
    cost = turnover * (fee + slippage)
    net = strat_ret - cost
    equity = capital * (1 + net).cumprod()
    trades = _extract_trades(df, pos_exec, fee + slippage)
    return {"equity": equity, "net_returns": net, "position": pos_exec, "trades": trades}

def _extract_trades(df, pos, cost):
    t = []; entry = None
    for i in range(1, len(pos)):
        if pos.iat[i] == 1 and pos.iat[i-1] == 0: entry = (df.index[i], df.open.iat[i])
        if pos.iat[i] == 0 and pos.iat[i-1] == 1 and entry:
            ex = df.open.iat[i]; pnl = (ex / entry[1] - 1) - 2 * cost
            t.append({"entry": entry[0], "exit": df.index[i], "entry_px": entry[1],
                      "exit_px": ex, "return": pnl, "days": (df.index[i] - entry[0]).days})
            entry = None
    return pd.DataFrame(t)
