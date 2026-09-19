import json
import os
from datetime import datetime, timezone

def log_trade(trade, strategy_params, log_path="monitoring/trade_log.jsonl"):
    """Append one trade record to a persistent, append-only log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    record = {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "entry": str(trade["entry"]),
        "exit": str(trade["exit"]),
        "entry_px": float(trade["entry_px"]),
        "exit_px": float(trade["exit_px"]),
        "return": float(trade["return"]),
        "days_held": int(trade["days"]),
        "params": strategy_params,
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")


def log_all_trades(trades_df, strategy_params, log_path="monitoring/trade_log.jsonl"):
    """Log every trade in a trades DataFrame (e.g. from run_backtest results)."""
    for _, trade in trades_df.iterrows():
        log_trade(trade, strategy_params, log_path)
