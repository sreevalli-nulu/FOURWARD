import pandas as pd
from backtest.sweep import sweep
from backtest.strategies import trendguard_signals
from backtest.engine import run_backtest


def walk_forward_backtest(df, train_window_days=550, retune_every_days=180,
                            fast_opts=(5, 8, 10, 12, 15),
                            slow_opts=(20, 30, 40, 50, 75),
                            atr_opts=(1.0, 1.5, 2.0, 2.5, 3.0),
                            fee=0.001, slippage=0.0005):
    """
    Re-tunes parameters periodically on a rolling window, instead of
    freezing one parameter set forever. Returns a stitched-together
    equity curve plus a log of which parameters were used in each window.
    """
    df = df.sort_index()
    start = df.index[0]
    end = df.index[-1]

    all_equity = []
    all_net_returns = []
    all_trades = []
    param_log = []

    window_start = start + pd.Timedelta(days=train_window_days)

    while window_start < end:
        train_slice = df[(df.index >= window_start - pd.Timedelta(days=train_window_days)) & (df.index < window_start)]
        window_end = min(window_start + pd.Timedelta(days=retune_every_days), end)
        live_slice = df[(df.index >= window_start) & (df.index < window_end)]

        if len(train_slice) < 100 or len(live_slice) == 0:
            window_start = window_end
            continue

        _, best = sweep(train_slice, fast_opts, slow_opts, atr_opts)
        fast, slow, atr_mult = int(best["fast"]), int(best["slow"]), float(best["atr_mult"])

        pos = trendguard_signals(live_slice, fast, slow, atr_mult)
        r = run_backtest(live_slice, pos, fee=fee, slippage=slippage)

        all_equity.append(r["equity"])
        all_net_returns.append(r["net_returns"])
        all_trades.append(r["trades"])
        param_log.append({"window_start": window_start, "window_end": window_end,
                           "fast": fast, "slow": slow, "atr_mult": atr_mult,
                           "train_calmar": float(best["Calmar"])})

        window_start = window_end

    equity = pd.concat(all_equity)
    net_returns = pd.concat(all_net_returns)
    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()

    return {"equity": equity, "net_returns": net_returns, "trades": trades,
            "param_log": pd.DataFrame(param_log)}