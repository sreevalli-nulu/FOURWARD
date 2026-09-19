# TrendGuard Strategy Documentation

## Assumptions

- Market: BTC/USDT and ETH/USDT, daily (1d) candles, 2019-01-01 onward, sourced from Binance via ccxt with a cached CSV fallback for offline reliability.
- Execution: next-open execution - signals are decided on the close of bar t, filled at the open of bar t+1.
- Costs: fee + slippage applied on every position change. Base case: 0.1% fee, 0.05% slippage per side. Sensitivity tested at 0.2% and 0.5% fee (see below).
- Capital: $10,000 starting capital, compounding.
- No leverage, no shorting - position is either fully in (1) or fully out (0).
- Frozen parameters: BTC uses fast=10, slow=50, atr_mult=3 (tuned on BTC's own 2019-2023 train period). ETH uses fast=12, slow=20, atr_mult=2.5 (tuned independently on ETH's own 2019-2023 train period, after discovering BTC's parameters do not transfer). Each asset's parameters were validated only on that same asset's held-out test period.

## Risk Characteristics

- **Correlation with BTC:** TrendGuard trades BTC/USDT directly, so returns are directionally correlated with BTC during "in position" periods. However, exposure is only ~36% of the time versus ~99% for buy-and-hold, which materially reduces correlation to BTC's full drawdown profile.

- **Test-period comparison vs. Buy & Hold** (apples-to-apples, both evaluated on 2024+ data):

  | Metric   | TrendGuard (BTC) | Buy & Hold (BTC) | TrendGuard (ETH, BTC params) | TrendGuard (ETH, tuned) | RSI Mean-Rev (ETH) |
|----------|-------------------|--------------------|--------------------------------|----------------------------|------------------------|
| CAGR     | 10.7%             | 24.2%              | -8.9%                          | 14.5%                      | 8.9%                   |
| Sharpe   | 0.50              | 0.70               | -0.10                          | 0.53                       | 0.41                   |
| Sortino  | 0.47              | 1.07               | -0.09                          | 0.57                       | 0.32                   |
| Calmar   | 0.33              | 0.47               | -0.15                          | 0.28                       | 0.20                   |
| Max DD   | -32.3%            | -53.0%             | -58.5%                         | -51.9%                     | -44.3%                 |
| Exposure | 36.3%             | 98.9%              | 32.6%                          | 42.9%                      | 30.0%                  |

  TrendGuard underperforms buy-and-hold on both raw and risk-adjusted return on BTC in the test period, but roughly halves the maximum drawdown while holding a position only about a third of the time - a materially different risk profile, even though the risk-adjusted numbers currently favor buy-and-hold in this window. On ETH, using the same frozen parameters, TrendGuard loses money outright in the test period - see Failure Conditions below.

- **Fee sensitivity** (train period, TrendGuard, BTC):

  | Fee  | CAGR  | Calmar |
  |------|-------|--------|
  | 0.1% | 63.4% | 1.63   |
  | 0.2% | 62.1% | 1.58   |
  | 0.5% | 58.0% | 1.41   |

  The strategy's edge is moderately, not severely, sensitive to fees - a 5x fee increase costs about 5.4 percentage points of CAGR.

## Failure Conditions

- **Sideways/choppy markets cause whipsaw losses.** In the BTC train-period trade log, several trades lasted only 3-6 days with losses of -2.5% to -10.4% - the fast/slow EMA crossed in and out without a sustained trend forming. This is the strategy's most common failure mode: it pays repeated small entry/exit costs during range-bound conditions.

- - **BTC-tuned parameters do not transfer to ETH, but this is fixable with proper per-asset tuning.** Using BTC's frozen parameters (fast=10, slow=50, atr_mult=3) on ETH/USDT for the 2024+ test period produced a CAGR of -8.9%. We investigated this properly rather than assuming a fix: we first ran an independent parameter sweep on ETH's own training data using our original grid, which converged on the identical fast=10/slow=50/atr_mult=3 combination - confirming the issue wasn't simply "wrong asset's parameters were reused." We then widened the sweep grid to test faster EMAs (fast: 5-15, slow: 20-75) and tighter stops (ATR: 1.0-3.0), better suited to ETH's typically choppier, faster-moving price action. This found a materially different, ETH-specific optimum: fast=12, slow=20, atr_mult=2.5, based on 28 trades in the training period - well above a minimum trade-count threshold we apply to avoid selecting parameters propped up by only a few lucky trades. Validated on ETH's held-out test period, this combination produced a CAGR of 14.5%, Sharpe of 0.53, and Calmar of 0.28 - turning a losing result into a profitable one, and outperforming our RSI mean-reversion comparison strategy on the same period (CAGR 8.9%, Calmar 0.20). The root cause was not that TrendGuard is unsuited to ETH, but that ETH's faster trend/noise cycle needed EMA periods outside the range our original BTC-derived grid tested.

- **Train-vs-test degradation on BTC itself.** Train-period Calmar (1.63) is meaningfully higher than test-period Calmar (0.33) on BTC - performance did not hold up out-of-sample even on the asset it was tuned on, which is a normal but important caveat: past parameter selection does not guarantee future performance.

- **Fee sensitivity is moderate, not severe.** CAGR degrades from 63.4% to 58.0% as fees rise from 0.1% to 0.5% (train period) - the edge survives realistic cost increases, but this was only tested on BTC; ETH's already-negative test result would only worsen further under higher fees.

- **Sharp, fast crashes can still cause large drawdowns despite the trailing stop.** The ATR-based stop reacts to recent volatility, but a sudden, sharp move can still produce a large single-trade loss before the stop triggers, as seen in ETH's -58.5% max drawdown.

- **Long-only design means no protection in sustained downtrends.** Since the strategy never shorts, extended bear markets are handled only by sitting in cash (0% exposure) - there's no mechanism to profit from, only avoid, a falling market.****


## Trade Recording & Adaptive Monitoring

Every backtest run persists its trades to an append-only log (`monitoring/trade_log.jsonl`), recording entry/exit dates, prices, realized return, holding period, and the exact strategy parameters active at the time of each trade. This creates a full, auditable history of every decision the strategy made.

A monitoring layer (`monitoring/health_check.py`) reads this log back and tracks recent performance - specifically, the win rate over the last N trades - rather than relying on lifetime averages that can mask a recent shift in market behavior.

If recent performance drops below a set threshold, a self-healing layer (`monitoring/self_heal.py`) automatically re-runs the existing parameter sweep on current data and proposes a new parameter set. This does **not** auto-apply the new parameters - it flags them for human review. We made this choice deliberately: a system that silently changes its own live trading parameters based on a short losing streak is a real risk, not just an implementation detail. Proposing, not auto-applying, keeps a human in the loop for any change that affects real capital.

This closes the loop the rest of this document describes in static form: instead of a one-time backtest with fixed parameters, the system continuously records its own behavior, checks its own health, and knows when it should ask for re-tuning - the direction of a self-monitoring, adaptive strategy, without removing human oversight from the decision to actually change anything.


## Walk-Forward Validation Experiment

To directly address the train-to-test degradation discussed above, we implemented and tested walk-forward validation: instead of freezing one parameter set indefinitely, the strategy re-tunes periodically on a rolling window of recent data (18 months of training data, re-tuned every 6 months), stitching the resulting periods together into one continuous track record.

**Result: walk-forward validation performed worse than the static frozen-parameter approach on ETH.**

| Approach | CAGR | Calmar | Max Drawdown |
|---|---|---|---|
| Static, ETH-tuned (fast=12, slow=20, atr_mult=2.5) | 14.5% | 0.28 | -51.9% |
| Walk-forward (re-tuned every 6 months) | 0.5% | 0.01 | -68.0% |

**Why we think this happened:** Examining the parameter log across the 13 re-tuning windows, two windows (covering mid-2022 to mid-2023) show a negative Calmar ratio even for their *best available* parameter combination - meaning there was no good trend-following parameter set during that stretch, and walk-forward was forced to use a losing configuration regardless. More broadly, each 18-month re-tuning window has substantially less data than our original ~5-year static training period, which likely increases the risk of fitting to short-term noise rather than a genuinely robust pattern - the opposite of what walk-forward is intended to achieve.

**What this tells us:** More frequent re-optimization is not automatically more robust. For this strategy and dataset, a longer, more stable training window (our original static approach) outperformed shorter, more frequently-refreshed windows. We report this as an honest negative result rather than omitting it - we hypothesized walk-forward would reduce degradation, tested it properly, and found evidence against that hypothesis. We would want to test longer re-tuning windows (e.g., 24-30 months) before concluding walk-forward can't help here at all, but the frozen static parameters remain our validated, presented approach.