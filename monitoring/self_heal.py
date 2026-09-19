from backtest.sweep import sweep
from monitoring.health_check import health_summary


def check_and_respond(df_price_data, log_path="monitoring/trade_log.jsonl", window=10):
    """
    Check recent trading health. If degrading, re-run the parameter sweep
    on the given price data and propose new parameters.

    This does NOT automatically apply new parameters — it flags them for
    human review, since auto-swapping live trading parameters without a
    human in the loop is a real risk, not just an implementation detail.
    """
    summary = health_summary(log_path, window)

    if not summary["degrading"]:
        return {
            "action": "hold",
            "reason": f"Recent win rate {summary['recent_win_rate']:.0%} is within healthy range.",
            "current_params": summary["current_params"],
            "proposed_params": None,
        }

    results, best = sweep(df_price_data)
    proposed = {
        "fast": int(best["fast"]),
        "slow": int(best["slow"]),
        "atr_mult": float(best["atr_mult"]),
    }

    return {
        "action": "propose_retune",
        "reason": f"Recent win rate {summary['recent_win_rate']:.0%} dropped below threshold — re-tuning suggested.",
        "current_params": summary["current_params"],
        "proposed_params": proposed,
        "proposed_calmar": float(best["Calmar"]),
    }
