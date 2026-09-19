\# TrendGuard Strategy Documentation



\## Assumptions

\- Market: BTC/USDT and ETH/USDT, daily (1d) candles, 2019-01-01 onward, sourced from Binance via ccxt with a cached CSV fallback for offline reliability.

\- Execution: next-open execution — signals are decided on the close of bar t, filled at the open of bar t+1.

\- Costs: fee + slippage applied on every position change. Base case: 0.1% fee, 0.05% slippage per side. Sensitivity tested at 0.2% and 0.5% fee (see below).

\- Capital: $10,000 starting capital, compounding.

\- No leverage, no shorting — position is either fully in (1) or fully out (0).



\## Risk Characteristics



\- \*\*Correlation with BTC:\*\* TrendGuard trades BTC/USDT directly, so returns are directionally correlated with BTC during "in position" periods. However, exposure is only \~36% of the time versus \~99% for buy-and-hold, which materially reduces correlation to BTC's full drawdown profile.



\- \*\*Test-period comparison vs. Buy \& Hold\*\* (apples-to-apples, both evaluated on 2024+ data):



&#x20; | Metric   | TrendGuard | Buy \& Hold |

&#x20; |----------|-----------|------------|

&#x20; | CAGR     | 10.7%     | 24.2%      |

&#x20; | Sharpe   | 0.50      | 0.70       |

&#x20; | Sortino  | 0.47      | 1.07       |

&#x20; | Calmar   | 0.33      | 0.47       |

&#x20; | Max DD   | -32.3%    | -53.0%     |

&#x20; | Exposure | 36.3%     | 98.9%      |



&#x20; TrendGuard underperforms buy-and-hold on both raw and risk-adjusted return in the test period, but roughly halves the maximum drawdown while holding a position only about a third of the time — a materially different risk profile, even though the risk-adjusted numbers currently favor buy-and-hold in this window.



\- \*\*Fee sensitivity\*\* (train period, TrendGuard):



&#x20; | Fee  | CAGR  |

