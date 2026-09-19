# TrendGuard - 3-Minute Demo Script

**0:00-0:15 - Open the app**

"This is TrendGuard, a systematic trend-following strategy for BTC and ETH."

Launch with `streamlit run app.py`.

**0:15-0:40 - Pick asset & period**

Select BTC/USDT, switch between train and test period in the sidebar.

"We train on data through 2023, and test entirely out-of-sample on 2024 onward - this keeps us honest."

**0:40-1:10 - Show equity curve**

Point out TrendGuard vs RSI mean-reversion vs Buy & Hold on the log-scale chart.

"Notice TrendGuard avoids the worst of the drawdowns here, even though it doesn't always keep pace on raw return."

**1:10-1:40 - Show metrics table + trade list**

Walk through Sharpe, Sortino, Calmar, and max drawdown side by side. Show a few real trades from the trade list.

**1:40-2:00 - Show AI report tab**

"This tab uses Claude to generate a plain-English summary grounded strictly in these exact numbers - no invented statistics."

**2:00-2:15 - The honest part**

Switch the asset selector to ETH, same parameters.

"Here's the part we think matters most: the exact same parameters that worked on BTC actually lose money on ETH. We're not hiding that - it's a real, honest finding about how far this strategy generalizes."

**2:15-2:45 - System Health tab**

Click into the System Health tab.

"Every backtest run logs its trades to a persistent record - entry, exit, return, and the exact parameters active at the time. The system tracks recent win rate, not just lifetime averages, so it can catch a real shift in performance early."

Click "Run Self-Check."

"If recent performance degrades, it automatically re-runs our parameter sweep and proposes new parameters - but it never applies them automatically. A human stays in the loop for any change to live trading behavior. This is our answer to 'how would this keep working over time.'"

**2:45-3:00 - Close**

"TrendGuard trades off some upside for meaningfully better drawdown control and far less time exposed to the market on BTC - and it's built to record its own behavior and flag when it needs re-tuning, rather than silently degrading over time."