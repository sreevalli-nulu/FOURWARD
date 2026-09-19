# TrendGuard

TrendGuard is a crypto trading strategy backtesting project.

## Features

- BTC/USDT and ETH/USDT backtesting
- Train and Test period selection
- EMA-based TrendGuard strategy
- RSI mean-reversion strategy
- Buy & Hold comparison
- Streamlit dashboard

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sreevalli-nulu/Open-Crypto-Trading-Strategy.git
cd Open-Crypto-Trading-Strategy
### 2. Create a virtual environment

python -m venv .venv
### 3. Activate the virtual environment

.venv\Scripts\activate
### 4. Install the required packages

pip install -r requirements.txt
### 5. Run the Streamlit app

streamlit run app.py
## Project Structure

- `app.py` — Streamlit dashboard
- `data/loader.py` — Loads cryptocurrency data
- `data/indicators.py` — Calculates technical indicators
- `data/raw/` — Stores BTC and ETH historical CSV data
- `strategy/` — Trading strategies
- `backtest/` — Backtesting functions
- `ai/` — AI report generation
## Data

The project uses daily OHLCV cryptocurrency data for BTC/USDT and ETH/USDT.

The dashboard can run using the committed CSV files, so it can work without a live API connection.

## Team

TrendGuard is a team project for cryptocurrency trading strategy backtesting.
