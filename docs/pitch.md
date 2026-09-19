# TrendGuard - Pitch Deck Outline

## Slide 1: Problem / Hook

Buy-and-hold crypto is volatile and emotionally brutal to hold through drawdowns. Can a rules-based, systematic strategy manage that risk better - even if it means giving up some upside?

## Slide 2: What TrendGuard Does

EMA crossover trend-following with an ATR-based trailing stop. Enters when a fast 20-period EMA crosses above a slower 50-period EMA, exits on the reverse cross or when price falls more than 3x ATR below the recent high. No prediction, no ML - just systematic trend capture with a defined exit rule.

## Slide 3: Backtest Methodology

Daily BTC/USDT and ETH/USDT candles, 2019-2026, from Binance via ccxt (cached CSV fallback for reliability). Train/test split at 2024-01-01. Next-open execution (signal on close, fill at next bar's open), with realistic fees (0.1% base case) and slippage (0.05%) applied on every position change.

## Slide 4: Results vs Buy-and-Hold

Test period (2024+): TrendGuard CAGR 10.7% vs Buy & Hold 24.2%. TrendGuard trails on raw return in this window.

## Slide 5: Risk-Adjusted Performance

Test period: Sharpe 0.50 vs 0.70, Calmar 0.33 vs 0.47 - buy-and-hold also wins on risk-adjusted return in this window.

Max drawdown: TrendGuard -32.3% vs Buy & Hold -53.0% - TrendGuard holds up meaningfully better in the worst case, while only being exposed to the market ~36% of the time vs ~99% for buy-and-hold.

## Slide 6: Where It Fails

The 2024+ test period was a regime where simply holding outperformed trend-following on both return and risk-adjusted metrics. TrendGuard's edge shows up in drawdown protection and reduced market exposure, not in return generation, during this window. It also underperforms in choppy, sideways markets where EMA crossovers generate frequent false signals.

On ETH, using the exact same frozen parameters tuned on BTC, TrendGuard produced a negative CAGR (-8.9%) and a larger max drawdown (-58.5%) than on BTC. This is a concrete example of parameter overfitting - a rule tuned on one asset does not automatically generalize to another, and we're reporting that honestly rather than cherry-picking only the BTC result.

## Slide 7: Adaptive Risk Monitoring

Every trade the strategy makes is logged persistently - entry, exit, return, and the exact parameters active at the time. A monitoring layer tracks recent win rate, not just lifetime averages, so it can catch a real shift in performance early.

If recent performance degrades, the system automatically re-runs its own parameter sweep and proposes new parameters - but never applies them automatically. A human stays in the loop for any change to live trading behavior. This is TrendGuard's answer to "how would this keep working over time": not a static, fire-and-forget backtest, but a system that records its own activity and knows when to ask for help.

## Slide 8: Live Demo Teaser

Watch the Streamlit app pick between BTC/ETH and train/test periods live, compare all three strategies (TrendGuard, RSI mean-reversion, Buy & Hold) on one equity curve, see an AI-generated plain-English report grounded strictly in the real backtest numbers, and check the System Health tab showing real trade logs and a live self-check.



Next steps: multi-asset expansion with independent parameter tuning per asset (informed directly by our ETH finding), live paper trading to validate against real-time execution, walk-forward re-optimization instead of a single static train/test split, and further robustness testing across the full parameter grid.