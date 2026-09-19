import itertools
import pandas as pd
from backtest.strategies import trendguard_signals
from backtest.engine import run_backtest
from backtest.metrics import metrics

def sweep(df_train, fast_opts=(10, 20, 30), slow_opts=(50, 100, 200), atr_opts=(2, 3, 4)):
    rows = []
    for fast, slow, atr_mult in itertools.product(fast_opts, slow_opts, atr_opts):
        if fast >= slow:
            continue  # skip nonsensical combos
        pos = trendguard_signals(df_train, fast, slow, atr_mult)
        r = run_backtest(df_train, pos)
        m = metrics(r["equity"], r["net_returns"])
        rows.append({"fast": fast, "slow": slow, "atr_mult": atr_mult, **m})
    results = pd.DataFrame(rows)
    best = results.loc[results["Calmar"].idxmax()]
    return results, best