import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
load_dotenv()



from backtest.strategies import trendguard_signals, rsi_meanrev_signals, buy_hold_signals
from backtest.engine import run_backtest
from backtest.metrics import metrics
from ai.report import explain_strategy
from monitoring.trade_logger import log_all_trades
from monitoring.self_heal import check_and_respond
from monitoring.health_check import health_summary

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

tab1, tab2, tab3 = st.tabs(["Backtest", "AI Risk Report", "System Health"])

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