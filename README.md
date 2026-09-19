# TrendGuard - Open Crypto Trading Strategy

A rules-based, long-only trend-following strategy for BTC and ETH, backtested honestly against Buy & Hold and an RSI mean-reversion variant - with per-asset tuned parameters, a live real-time signal, an AI-generated plain-English risk report, and a self-monitoring system that flags when re-tuning may be needed.

Built for the Multipli Hackathon - "Open Crypto Trading Strategy."

## For judges - quickest way to run this

```powershell
git clone https://github.com/sreevalli-nulu/Open-Crypto-Trading-Strategy.git
cd Open-Crypto-Trading-Strategy
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

This opens the app at `http://localhost:8501`. The **Backtest**, **System Health**, and **Live Signal** tabs work immediately with no further setup. The **AI Risk Report** tab needs an Anthropic API key (see below) - every other tab works without one.

*(Mac/Linux: use `source .venv/bin/activate` instead of `.venv\Scripts\activate`.)*

## What it does

TrendGuard enters a position when a fast EMA crosses above a slower EMA (with a price confirmation filter), and exits either on the reverse cross or via an ATR-based trailing stop. No leverage, no shorting, no ML prediction - a transparent, explainable rule, tested against real historical data with real fees and slippage, and validated separately on each asset.

We found that BTC-tuned parameters do not transfer to ETH - the same settings that work well on BTC actually lose money on ETH. Rather than force one setting onto both assets, we ran an independent parameter sweep on each asset's own data and validated each on its own held-out test period. See `docs/strategy.md` for the full assumptions, risk characteristics, and failure conditions - including this finding and a walk-forward validation experiment we ran to test whether periodic re-tuning would reduce out-of-sample performance decay (it didn't, and we explain why).

**Frozen parameters, validated independently per asset:**
- **BTC:** fast=10, slow=50, atr_mult=3
- **ETH:** fast=12, slow=20, atr_mult=2.5

## Enabling the AI Risk Report tab (optional)

Create a file named `.env` in the project root (a template is provided as `.env.example`) containing:
LLM_API_KEY=your-anthropic-api-key-here
This loads automatically every time the app runs - no manual environment variable needed. Without a key, every other tab still works normally; only the AI Risk Report tab will show a message explaining a key is needed.

## What each tab shows

- **Backtest** - equity curve comparing TrendGuard, RSI mean-reversion, and Buy & Hold, plus a metrics table (CAGR, Sharpe, Sortino, Calmar, drawdown, exposure) and TrendGuard's individual trade list. Switch between BTC/ETH and Train/Test/Full periods with the sidebar controls.
- **AI Risk Report** - generates a plain-English summary of the current backtest results using Claude, grounded strictly in the real numbers provided (never invented statistics).
- **System Health** - shows how many trades have been persistently logged, the recent win rate, and a health status. The "Run Self-Check" button checks recent performance and, if it has degraded, proposes new parameters via a fresh sweep - it never applies a change automatically, only proposes one for human review.
- **Live Signal** - pulls real, current market data (via the same public Binance API used for historical data) and shows what TrendGuard would decide right now, auto-refreshing every 60 seconds. Includes a live paper-trading ledger that logs simulated trades as the signal changes over time, building a real, timestamped track record. This is an informational paper simulation only - no real trades are ever placed.

## Project structure
Open-Crypto-Trading-Strategy/
├── app.py # Streamlit dashboard (all four tabs)
├── data/
│ ├── loader.py # Fetches historical OHLCV via ccxt, with CSV fallback
│ ├── live_feed.py # Fetches current live price/candles, builds the live recommendation
│ ├── indicators.py # EMA, ATR, RSI
│ └── raw/ # Cached BTC/ETH daily CSVs (real data, committed for offline reliability)
├── backtest/
│ ├── strategies.py # TrendGuard, RSI mean-reversion, Buy & Hold signal functions
│ ├── engine.py # Backtest engine (next-open execution, fees + slippage)
│ ├── metrics.py # CAGR, Sharpe, Sortino, Calmar, drawdown, etc.
│ ├── sweep.py # Parameter grid search, with a minimum-trade-count reliability filter
│ └── walkforward.py # Walk-forward re-optimization experiment (see docs/strategy.md for result)
├── monitoring/
│ ├── trade_logger.py # Persists every backtest trade to an append-only log
│ ├── health_check.py # Reads the trade log, calculates recent win rate
│ ├── self_heal.py # Proposes (never auto-applies) new parameters if performance degrades
│ └── live_paper_trader.py # Logs simulated live trades and tracks a running virtual balance
├── ai/
│ └── report.py # Generates the AI risk report via the Anthropic API
├── docs/
│ ├── strategy.md # Assumptions, risk characteristics, failure conditions, ETH fix, walk-forward experiment
│ ├── pitch.md # Pitch deck outline
│ └── demo_script.md # Timed live demo script
└── tests/
└── test_engine.py # Unit tests verifying engine correctness


## Key results (test period, 2024+)

| Metric   | TrendGuard (BTC) | Buy & Hold (BTC) | TrendGuard (ETH, tuned) | RSI Mean-Rev (ETH) |
|----------|-------------------|--------------------|----------------------------|------------------------|
| CAGR     | 10.7%             | 24.2%              | 14.5%                       | 8.9%                   |
| Sharpe   | 0.50              | 0.70               | 0.53                        | 0.41                   |
| Calmar   | 0.33              | 0.47               | 0.28                        | 0.20                   |
| Max DD   | -32.3%            | -53.0%             | -51.9%                      | -44.3%                 |
| Exposure | 36.3%             | 98.9%              | 42.9%                       | 30.0%                  |

TrendGuard trades off some raw return for meaningfully better drawdown control on BTC. On ETH, using properly asset-specific tuned parameters, TrendGuard outperforms both a naive parameter transfer from BTC and our RSI mean-reversion comparison. Full analysis, including honest reporting of train-to-test performance degradation and a walk-forward validation experiment, is in `docs/strategy.md`.

## Team Fourward

Sreevalli Nulu-25BCB0050
Anumita-25BCB0097
Rashi Shrivastava-25BCB0064
