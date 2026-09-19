import pandas as pd, numpy as np
from backtest.engine import run_backtest
from backtest.strategies import buy_hold_signals

def test_buy_hold_matches_price_ratio():
    idx = pd.date_range("2020-01-01", periods=100, freq="D")
    px = pd.Series(np.linspace(100, 200, 100), index=idx)
    df = pd.DataFrame({"open": px, "high": px, "low": px, "close": px, "volume": 1}, index=idx)
    r = run_backtest(df, buy_hold_signals(df), fee=0, slippage=0, capital=1000)
    assert abs(r["equity"].iloc[-1] / 1000 - px.iloc[-1] / px.iloc[1]) < 0.02

def test_flat_strategy_keeps_capital():
    idx = pd.date_range("2020-01-01", periods=50, freq="D")
    px = pd.Series(np.random.rand(50) * 100 + 100, index=idx)
    df = pd.DataFrame({"open": px, "high": px, "low": px, "close": px, "volume": 1}, index=idx)
    r = run_backtest(df, pd.Series(0, index=idx), fee=0.001, capital=1000)
    assert abs(r["equity"].iloc[-1] - 1000) < 1e-6