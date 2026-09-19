# TrendGuard - 3-Minute Demo Script

**0:00-0:20 - Open the app**

"This is TrendGuard, a systematic trend-following strategy for BTC and ETH."

Launch with `streamlit run app.py`.

**0:20-0:50 - Pick asset & period**

Select BTC/USDT, switch between train and test period in the sidebar.

"We train on data through 2023, and test entirely out-of-sample on 2024 onward - this keeps us honest."

**0:50-1:30 - Show equity curve**

Point out TrendGuard vs RSI mean-reversion vs Buy & Hold on the log-scale chart.

"Notice TrendGuard avoids the worst of the drawdowns here, even though it doesn't always keep pace on raw return."

**1:30-2:10 - Show metrics table + trade list**

Walk through Sharpe, Sortino, Calmar, and max drawdown side by side. Show a few real trades from the trade list.

**2:10-2:35 - Show AI report tab**

"This tab uses Claude to generate a plain-English summary grounded strictly in these exact numbers - no invented statistics."

**2:35-2:50 - The honest part**

Switch the asset selector to ETH, same parameters.

"Here's the part we think matters most: the exact same parameters that worked on BTC actually lose money on ETH. We're not hiding that - it's a real, honest finding about how far this strategy generalizes."

**2:50-3:00 - Close**

"TrendGuard trades off some upside for meaningfully better drawdown control and far less time exposed to the market on BTC - but it's a reminder that a backtest result on one asset is not a guarantee on another."