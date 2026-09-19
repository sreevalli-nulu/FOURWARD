from pathlib import Path
from datetime import datetime, timezone

import ccxt
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "raw"

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def _csv_path(symbol, timeframe):
    filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
    return RAW_DIR / filename


def _parse_since(exchange, since):
    if isinstance(since, int):
        return since

    if isinstance(since, datetime):
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        return int(since.timestamp() * 1000)

    since = str(since)

    if len(since) == 10:
        since = since + "T00:00:00Z"

    return exchange.parse8601(since)


def _load_cached_csv(path):
    df = pd.read_csv(path)

    if "timestamp" not in df.columns:
        raise ValueError(f"Cached CSV is missing the timestamp column: {path}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df


def fetch_ohlcv(symbol, timeframe, since):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = _csv_path(symbol, timeframe)

    exchange = ccxt.binance({
        "enableRateLimit": True
    })

    try:
        since_ms = _parse_since(exchange, since)
        all_candles = []
        current_since = since_ms

        while True:
            candles = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=current_since,
                limit=1000
            )

            if not candles:
                break

            all_candles.extend(candles)

            if len(candles) < 1000:
                break

            last_timestamp = candles[-1][0]
            next_since = last_timestamp + 1

            if next_since <= current_since:
                break

            current_since = next_since

        if not all_candles:
            raise ValueError("Binance returned no OHLCV data.")

        df = pd.DataFrame(all_candles, columns=COLUMNS)

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

        df = df.drop_duplicates(subset="timestamp")
        df = df.sort_values("timestamp").reset_index(drop=True)

        return df

    except Exception as error:
        print(f"Binance API failed: {error}")

        if csv_path.exists():
            print(f"Using cached data: {csv_path}")
            return _load_cached_csv(csv_path)

        raise RuntimeError(
            f"Binance API failed and no cached CSV exists at {csv_path}"
        ) from error


def save_ohlcv(df, symbol, timeframe):
    csv_path = _csv_path(symbol, timeframe)

    df.to_csv(csv_path, index=False)

    print(f"Saved {len(df)} rows to {csv_path}")


if __name__ == "__main__":
    for symbol in ["BTC/USDT", "ETH/USDT"]:
        print(f"\nFetching {symbol}...")

        df = fetch_ohlcv(
            symbol=symbol,
            timeframe="1d",
            since="2019-01-01"
        )

        save_ohlcv(
            df=df,
            symbol=symbol,
            timeframe="1d"
        )

        print(df.head())
        print(df.tail())