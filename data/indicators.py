import pandas as pd


def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    previous_close = df["close"].shift(1)

    high_low = df["high"] - df["low"]
    high_previous_close = (df["high"] - previous_close).abs()
    low_previous_close = (df["low"] - previous_close).abs()

    true_range = pd.concat(
        [high_low, high_previous_close, low_previous_close],
        axis=1
    ).max(axis=1)

    return true_range.rolling(n).mean()


def rsi(series, n=14):
    change = series.diff()

    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)

    average_gain = gain.rolling(n).mean()
    average_loss = loss.rolling(n).mean()

    relative_strength = average_gain / average_loss

    return 100 - (100 / (1 + relative_strength))