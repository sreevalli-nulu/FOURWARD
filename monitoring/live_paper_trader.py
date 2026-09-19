import json
import os
from datetime import datetime, timezone

LEDGER_PATH = "monitoring/live_paper_ledger.json"


def _load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"open_position": None, "closed_trades": [], "starting_capital": 10000}
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def _save_ledger(ledger):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def update_live_ledger(asset, current_position, current_price):
    """
    Call this every time the live tab refreshes. It compares the new
    signal to what the ledger last recorded, and logs a simulated
    entry/exit only when the signal actually changes.
    """
    ledger = _load_ledger()
    now = datetime.now(timezone.utc).isoformat()

    if current_position == 1 and ledger["open_position"] is None:
        # New entry
        ledger["open_position"] = {
            "asset": asset,
            "entry_price": current_price,
            "entry_time": now,
        }

    elif current_position == 0 and ledger["open_position"] is not None:
        # Close the open position
        entry = ledger["open_position"]
        trade_return = (current_price / entry["entry_price"]) - 1
        ledger["closed_trades"].append({
            "asset": entry["asset"],
            "entry_price": entry["entry_price"],
            "entry_time": entry["entry_time"],
            "exit_price": current_price,
            "exit_time": now,
            "return": trade_return,
        })
        ledger["open_position"] = None

    _save_ledger(ledger)
    return ledger


def get_ledger_summary():
    ledger = _load_ledger()
    closed = ledger["closed_trades"]
    capital = ledger["starting_capital"]
    for t in closed:
        capital *= (1 + t["return"])

    return {
        "starting_capital": ledger["starting_capital"],
        "current_capital": capital,
        "num_closed_trades": len(closed),
        "open_position": ledger["open_position"],
        "closed_trades": closed,
    }