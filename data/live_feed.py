import ccxt
import pandas as pd
from datetime import datetime, timezone

_exchange = ccxt.binance()

SYMBOL_MAP = {"BTC": "BTC/USDT", "ETH": "ETH/USDT"}


def fetch_current_price(asset="BTC"):
    """Fetch the current live price for BTC or ETH."""
    symbol = SYMBOL_MAP[asset]
    ticker = _exchange.fetch_ticker(symbol)
    return {
        "asset": asset,
        "price": ticker["last"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bid": ticker["bid"],
        "ask": ticker["ask"],
    }


def fetch_recent_candles(asset="BTC", timeframe="1d", limit=250):
    """Fetch the most recent candles, same shape as your historical CSVs."""
    symbol = SYMBOL_MAP[asset]
    ohlcv = _exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp")
    return df

def build_recommendation(live_signals, current_price):
    """Turn the live signal into a short, plain-English status description."""
    current_position = live_signals.iloc[-1]
    prev_position = live_signals.iloc[-2] if len(live_signals) > 1 else current_position

    just_changed = current_position != prev_position

    if current_position == 1 and just_changed:
        return {
            "status": "ENTRY SIGNAL",
            "color": "success",
            "message": f"TrendGuard just signaled entry — the fast EMA crossed above the slow EMA. If following this strategy exactly, this is when a position would be opened at approximately ${current_price:,.2f}."
        }
    elif current_position == 1 and not just_changed:
        days_in = int((live_signals == 1)[::-1].to_numpy().argmin() or len(live_signals))
        return {
            "status": "HOLDING",
            "color": "info",
            "message": f"TrendGuard is currently in a long position, held for {days_in} day(s) so far. No new action - the strategy stays in until an exit condition triggers."
        }
    elif current_position == 0 and just_changed:
        return {
            "status": "EXIT SIGNAL",
            "color": "warning",
            "message": f"TrendGuard just signaled exit — either the trend reversed or the trailing stop triggered. If following this strategy exactly, a held position would be closed at approximately ${current_price:,.2f}."
        }
    else:
        return {
            "status": "FLAT / WAITING",
            "color": "info",
            "message": "TrendGuard is currently flat (in cash), waiting for the next entry signal - a fast EMA crossing above the slow EMA."
        }