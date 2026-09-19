# TrendGuard - Open Crypto Trading Strategy

A rules-based, long-only trend-following strategy for BTC and ETH, backtested honestly against Buy & Hold and an RSI mean-reversion variant - with an AI-generated plain-English risk report grounded strictly in real backtest numbers.

Built for the Multipli Hackathon, Round 1 - "Open Crypto Trading Strategy."

## What it does

TrendGuard enters a position when a fast EMA crosses above a slower EMA (with a price confirmation filter), and exits either on the reverse cross or via an ATR-based trailing stop. No leverage, no shorting, no ML prediction - just a transparent, explainable rule, tested against real historical data with real fees and slippage.

See `docs/strategy.md` for the full assumptions, risk characteristics, and failure conditions - including an honest finding that the strategy's BTC-tuned parameters do not generalize cleanly to ETH.

## Setup

```powershell
git clone https://github.com/sreevalli-nulu/Open-Crypto-Trading-Strategy.git
cd Open-Crypto-Trading-Strategy
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set your Anthropic API key (needed only for the AI Risk Report tab):
```powershell
$env:LLM_API_KEY = "your-key-here"
```

## Run it

```powershell
streamlit run app.py
```

Opens at `http://localhost:8501`. Pick an asset (BTC/ETH), a period (train/test/full), and adjust strategy parameters live. The AI Risk Report tab generates a fresh plain-English summary from the current backtest results.

## Project structure
Open-Crypto-Trading-Strategy/
├── app.py # Streamlit dashboard
├── data/
│ ├── loader.py # Fetches OHLCV data via ccxt, with CSV fallback
│ ├── indicators.py # EMA, ATR, RSI
│ └── raw/ # Cached BTC/ETH daily CSVs (real data, committed for offline reliability)
├── backtest/
│ ├── strategies.py # TrendGuard, RSI mean-reversion, Buy & Hold signal functions
│ ├── engine.py # Backtest engine (next-open execution, fees + slippage)
│ ├── metrics.py # CAGR, Sharpe, Sortino, Calmar, drawdown, etc.
│ └── sweep.py # Parameter grid search over the train period
├── ai/
│ └── report.py # Generates the plain-English AI risk report via the Anthropic API
├── docs/
│ ├── strategy.md # Assumptions, risk characteristics, failure conditions
│ ├── pitch.md # 8-slide pitch outline
│ └── demo_script.md # 3-minute live demo script
└── tests/
└── test_engine.py # Unit tests verifying engine correctness


## Key results (test period, 2024+)

| Metric   | TrendGuard (BTC) | Buy & Hold (BTC) | TrendGuard (ETH) |
|----------|-------------------|--------------------|--------------------|
| CAGR     | 10.7%             | 24.2%              | -8.9%              |
| Max DD   | -32.3%            | -53.0%             | -58.5%             |
| Exposure | 36.3%             | 98.9%              | 32.6%              |

TrendGuard trades off some raw return for meaningfully better drawdown control on BTC - but the same frozen parameters do not generalize to ETH, which we report honestly rather than hide. Full analysis in `docs/strategy.md`.

