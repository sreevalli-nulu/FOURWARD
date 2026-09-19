import numpy as np, pandas as pd
from data.indicators import ema, atr, rsi

def trendguard_signals(df, fast=20, slow=50, atr_mult=3.0):
    d = df.copy()
    d["ema_f"], d["ema_s"], d["atr"] = ema(d.close, fast), ema(d.close, slow), atr(d)
    pos = np.zeros(len(d)); in_pos = False; peak = 0.0
    for i in range(1, len(d)):
        c, ef, es, a = d.close.iat[i], d.ema_f.iat[i], d.ema_s.iat[i], d.atr.iat[i]
        if not in_pos:
            if ef > es and d.ema_f.iat[i-1] <= d.ema_s.iat[i-1] and c > es:
                in_pos, peak = True, c
        else:
            peak = max(peak, c)
            if ef < es or c < peak - atr_mult * a:
                in_pos = False
        pos[i] = 1 if in_pos else 0
    return pd.Series(pos, index=d.index, name="position")

def rsi_meanrev_signals(df, n=14, buy_below=30, sell_above=55):
    r = rsi(df.close, n); pos = np.zeros(len(df)); in_pos = False
    for i in range(1, len(df)):
        if not in_pos and r.iat[i] < buy_below: in_pos = True
        elif in_pos and r.iat[i] > sell_above: in_pos = False
        pos[i] = int(in_pos)
    return pd.Series(pos, index=df.index, name="position")

def buy_hold_signals(df):
    return pd.Series(1, index=df.index, name="position")