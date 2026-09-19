import streamlit as st
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="TrendGuard",
    page_icon="📈",
    layout="wide"
)

st.title("TrendGuard")
st.write("Crypto Trading Strategy Backtesting Dashboard")
st.sidebar.header("Strategy Controls")

asset = st.sidebar.selectbox(
    "Asset",
    ["BTC/USDT", "ETH/USDT"]
)
period = st.sidebar.selectbox(
    "Period",
    ["Train", "Test"]
)
ema_fast = st.sidebar.number_input(
    "EMA Fast",
    min_value=1,
    value=20,
    step=1
)

ema_slow = st.sidebar.number_input(
    "EMA Slow",
    min_value=1,
    value=50,
    step=1
)

atr_multiplier = st.sidebar.number_input(
    "ATR Multiplier",
    min_value=0.1,
    value=2.0,
    step=0.1
)
fee_per_side = st.sidebar.number_input(
    "Fee per Side",
    min_value=0.0,
    value=0.001,
    step=0.0001,
    format="%.4f"
)



BASE_DIR = Path(__file__).resolve().parent

if asset == "BTC/USDT":
    data_file = BASE_DIR / "data" / "raw" / "BTC_USDT_1d.csv"
else:
    data_file = BASE_DIR / "data" / "raw" / "ETH_USDT_1d.csv"

df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
train_df = df[df["timestamp"].dt.year < 2024].copy()
test_df = df[df["timestamp"].dt.year >= 2024].copy()

if period == "Train":
    selected_df = train_df
else:
    selected_df = test_df
    st.subheader(f"{asset} — {period} Data")

st.write(
    f"Rows: {len(selected_df)} | "
    f"From: {selected_df['timestamp'].min().date()} | "
    f"To: {selected_df['timestamp'].max().date()}"
)

st.dataframe(selected_df.tail(10), use_container_width=True)
st.subheader("Price Chart")

st.line_chart(
    selected_df.set_index("timestamp")["close"]
)