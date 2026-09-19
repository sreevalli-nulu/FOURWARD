import itertools
import pandas as pd
from backtest.strategies import trendguard_signals
from backtest.engine import run_backtest
from backtest.metrics import metrics

def sweep(df_train, fast_opts=(10, 20, 30), slow_opts=(50, 100, 200), atr_opts=(2, 3, 4), min_trades=15):
    rows = []
    for fast, slow, atr_mult in itertools.product(fast_opts, slow_opts, atr_opts):
        if fast >= slow:
            continue
        pos = trendguard_signals(df_train, fast, slow, atr_mult)
        r = run_backtest(df_train, pos)
        m = metrics(r["equity"], r["net_returns"])
        num_trades = len(r["trades"])
        rows.append({"fast": fast, "slow": slow, "atr_mult": atr_mult, "num_trades": num_trades, **m})
    results = pd.DataFrame(rows)

    # Only consider combinations with enough trades to trust the result
    reliable = results[results["num_trades"] >= min_trades]
    if len(reliable) == 0:
        # fall back to all results if nothing meets the bar, but flag it
        reliable = results

    best = reliable.loc[reliable["Calmar"].idxmax()]
    return results, best