import json
import pandas as pd

def load_trade_log(log_path="monitoring/trade_log.jsonl"):
    """Read the trade log back into a DataFrame."""
    rows = [json.loads(line) for line in open(log_path)]
    return pd.DataFrame(rows)


def recent_win_rate(df, n=10):
    """Win rate over the last n trades."""
    recent = df.tail(n)
    if len(recent) == 0:
        return None
    return (recent["return"] > 0).mean()


def recent_avg_return(df, n=10):
    """Average return over the last n trades."""
    recent = df.tail(n)
    if len(recent) == 0:
        return None
    return recent["return"].mean()


def is_degrading(df, window=10, win_rate_threshold=0.3):
    """Flag if recent win rate has dropped below a healthy threshold."""
    wr = recent_win_rate(df, window)
    if wr is None:
        return False
    return wr < win_rate_threshold


def health_summary(log_path="monitoring/trade_log.jsonl", window=10):
    """One-call summary of recent trading health."""
    df = load_trade_log(log_path)
    return {
        "total_trades_logged": len(df),
        "recent_win_rate": recent_win_rate(df, window),
        "recent_avg_return": recent_avg_return(df, window),
        "degrading": is_degrading(df, window),
        "current_params": df.iloc[-1]["params"] if len(df) else None,
    }

