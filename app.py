import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
load_dotenv()

from data.live_feed import fetch_current_price, fetch_recent_candles, build_recommendation
from backtest.strategies import trendguard_signals, rsi_meanrev_signals, buy_hold_signals
from backtest.engine import run_backtest
from backtest.metrics import metrics
from ai.report import explain_strategy
from monitoring.trade_logger import log_all_trades
from monitoring.self_heal import check_and_respond
from monitoring.health_check import health_summary
from monitoring.live_paper_trader import update_live_ledger, get_ledger_summary
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="TrendGuard", layout="wide")
st.title("TrendGuard — Crypto Trading Strategy Backtest")

# --- Sidebar controls ---
st.sidebar.header("Settings")
asset = st.sidebar.selectbox("Asset", ["BTC", "ETH"])
fast = st.sidebar.slider("EMA fast", 5, 40, 10)
slow = st.sidebar.slider("EMA slow", 40, 250, 50)
atr_mult = st.sidebar.slider("ATR multiplier", 1.0, 5.0, 3.0, step=0.5)
fee = st.sidebar.number_input("Fee per side (%)", value=0.1, step=0.05) / 100

# --- Load data ---
file_map = {"BTC": "data/raw/BTC_USDT_1d.csv", "ETH": "data/raw/ETH_USDT_1d.csv"}
df = pd.read_csv(file_map[asset], index_col="timestamp", parse_dates=True)
df_train = df[df.index < "2024-01-01"]
df_test = df[df.index >= "2024-01-01"]

def run_all(data):
    strategies = {
        "TrendGuard": trendguard_signals(data, fast, slow, atr_mult),
        "RSI Mean-Reversion": rsi_meanrev_signals(data),
        "Buy & Hold": buy_hold_signals(data),
    }
    return {name: run_backtest(data, pos, fee=fee) for name, pos in strategies.items()}

tab1, tab2, tab3, tab4 = st.tabs(["Backtest", "AI Risk Report", "System Health", "Live Signal"])

with tab1:
    period = st.radio("Period", ["Train (2019–2023)", "Test (2024–now)", "Full"], horizontal=True)
    data = df_train if period.startswith("Train") else df_test if period.startswith("Test") else df

    results = run_all(data)
    log_all_trades(results["TrendGuard"]["trades"], {"fast": fast, "slow": slow, "atr_mult": atr_mult})

    fig = go.Figure()
    for name, r in results.items():
        fig.add_trace(go.Scatter(x=r["equity"].index, y=r["equity"], mode="lines", name=name))
    fig.update_layout(title=f"{asset} — Equity Curve ({period})", yaxis_type="log", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Performance Metrics")
    metrics_table = pd.DataFrame({name: metrics(r["equity"], r["net_returns"]) for name, r in results.items()}).T
    st.dataframe(metrics_table.style.format("{:.3f}"))

    st.subheader("TrendGuard Trades")
    st.dataframe(results["TrendGuard"]["trades"])

with tab2:
    st.write("Generates a plain-English risk report using the frozen parameters (fast=10, slow=50, atr_mult=3).")

    if not os.environ.get("LLM_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        st.warning("No API key found. Create a `.env` file in the project root with `LLM_API_KEY=your-key-here` to enable this tab. See README.md for setup instructions.")
    else:
        if st.button("Generate AI Report"):
            with st.spinner("Asking Claude..."):
                r_train = run_backtest(df_train, trendguard_signals(df_train, 10, 50, 3), fee=fee)
                r_test = run_backtest(df_test, trendguard_signals(df_test, 10, 50, 3), fee=fee)
                r_bench = run_backtest(df_test, buy_hold_signals(df_test), fee=fee)

                m_train = metrics(r_train["equity"], r_train["net_returns"])
                m_test = metrics(r_test["equity"], r_test["net_returns"])
                m_bench = metrics(r_bench["equity"], r_bench["net_returns"])

                rules = """TrendGuard uses a fast EMA and slow EMA.
Entry: fast EMA crosses above slow EMA, and price is above the slow EMA.
Exit: fast EMA crosses below slow EMA, OR price falls below the highest price since entry minus ATR multiplier times ATR.
The strategy is long-only. It does not short. It does not use leverage."""

                try:
                    report = explain_strategy(rules, m_train, m_test, m_bench)
                    st.success("Report generated")
                    st.write(report)
                except Exception as e:
                    st.error(f"Could not generate report: {e}")
        else:
            st.info("Click the button to generate a fresh AI risk report using live backtest metrics.")

with tab3:
    st.subheader("System Health — Trade Recording & Adaptive Monitoring")
    st.write("Every backtest run logs its trades to a persistent record. The system checks recent performance and flags when re-tuning may be needed.")

    try:
        summary = health_summary()
        col1, col2, col3 = st.columns(3)
        col1.metric("Trades logged", summary["total_trades_logged"])
        col2.metric("Recent win rate", f"{summary['recent_win_rate']:.0%}" if summary["recent_win_rate"] is not None else "N/A")
        col3.metric("Status", "Degrading" if summary["degrading"] else "Healthy")

        if st.button("Run Self-Check"):
            with st.spinner("Checking recent performance and re-tuning if needed..."):
                response = check_and_respond(df)
                st.write(f"**Action:** {response['action']}")
                st.write(f"**Reason:** {response['reason']}")
                st.write(f"**Current parameters:** {response['current_params']}")
                if response["proposed_params"]:
                    st.warning(f"Proposed new parameters (requires human approval before applying): {response['proposed_params']}")
                else:
                    st.success("No re-tuning needed.")
    except FileNotFoundError:
        st.info("No trades logged yet — run a backtest in the Backtest tab first.")

with tab4:
    st_autorefresh(interval=60000, key="live_refresh")
    st.subheader("Live Signal — Real-Time Market Data")
    st.write("Pulls current market data and shows what TrendGuard would decide right now. This is a live paper simulation, not real trading.")

    live_asset = st.selectbox("Asset (live)", ["BTC", "ETH"], key="live_asset")
    st.caption("Auto-refreshing every 60 seconds.")

    try:
        current = fetch_current_price(live_asset)
        df_live = fetch_recent_candles(live_asset, timeframe="1d", limit=250)
        live_signals = trendguard_signals(df_live, 10, 50, 3)
        current_position = live_signals.iloc[-1]

        update_live_ledger(live_asset, current_position, current["price"])

        col1, col2, col3 = st.columns(3)
        col1.metric(f"{live_asset} current price", f"${current['price']:,.2f}")
        col2.metric("Position", "IN (long)" if current_position == 1 else "OUT (flat)")
        col3.metric("As of", current["timestamp"][:19].replace("T", " ") + " UTC")

        rec = build_recommendation(live_signals, current["price"])
        if rec["color"] == "success":
            st.success(f"**{rec['status']}**\n\n{rec['message']}")
        elif rec["color"] == "warning":
            st.warning(f"**{rec['status']}**\n\n{rec['message']}")
        else:
            st.info(f"**{rec['status']}**\n\n{rec['message']}")

        st.caption("This is an informational signal based on the strategy's own rules, not financial advice. It shows what the strategy indicates - any decision to act is yours.")

        st.subheader("Live Paper-Trading Ledger")
        ledger_summary = get_ledger_summary()
        lcol1, lcol2, lcol3 = st.columns(3)
        lcol1.metric("Virtual capital", f"${ledger_summary['current_capital']:,.2f}",
                     f"{(ledger_summary['current_capital'] / ledger_summary['starting_capital'] - 1) * 100:+.2f}%")
        lcol2.metric("Closed trades", ledger_summary["num_closed_trades"])
        lcol3.metric("Open position", "Yes" if ledger_summary["open_position"] else "No")

        if ledger_summary["closed_trades"]:
            st.dataframe(pd.DataFrame(ledger_summary["closed_trades"]))
        else:
            st.caption("No trades completed yet in live tracking - this builds up over time as the signal changes.")

        fig_live = go.Figure()
        fig_live.add_trace(go.Scatter(x=df_live.index, y=df_live["close"], mode="lines", name="Price"))
        fig_live.update_layout(title=f"{live_asset} — Last 250 Days (Live)", height=400)
        st.plotly_chart(fig_live, use_container_width=True)

        st.caption("This shows what the strategy would decide right now, using real current market data. It is a paper simulation only — no real trades are placed.")
    except Exception as e:
        st.error(f"Could not fetch live data: {e}")