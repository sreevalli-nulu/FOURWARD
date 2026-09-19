import os
import anthropic

api_key = os.environ.get("LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    raise RuntimeError("No API key found. Set LLM_API_KEY or ANTHROPIC_API_KEY first.")

client = anthropic.Anthropic(api_key=api_key)


SYSTEM_PROMPT = """You are writing a plain-English report on a crypto trading strategy backtest.

CRITICAL RULES:
- Only use the exact numbers provided in the metrics.
- Never invent numbers.
- Never estimate missing numbers.
- Never change the meaning of a number.
- If a number is not provided, say that it is not available.
- Be honest, not promotional.
- If test performance is worse than training performance, state that clearly.
- Write approximately 250 words.
- Use plain English.
- Explain technical terms briefly when necessary.

Your report MUST cover these four sections in this order:

1. What the strategy does
Explain the strategy mechanically in 1-2 sentences.

2. Risk-adjusted comparison vs buy-and-hold
Discuss the available CAGR, Sharpe, Sortino, Calmar, and maximum drawdown numbers.
Use the actual supplied numbers.

3. Train-vs-test honesty
Compare the training metrics with the testing metrics.
Clearly state whether performance improves, remains similar, or degrades.

4. Where it fails
Explain market conditions where this strategy may struggle, based on the strategy rules.
Do not invent backtest results.
"""


def explain_strategy(
    rules: str,
    metrics_train: dict,
    metrics_test: dict,
    bench: dict
) -> str:

    user_content = f"""Strategy rules:
{rules}

Train period metrics:
{metrics_train}

Test period metrics:
{metrics_test}

Buy-and-hold benchmark metrics:
{bench}

Write the approximately 250-word report now.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_content
            }
        ]
    )

    return response.content[0].text


def explain_strategy_cached(
    rules: str,
    metrics_train: dict,
    metrics_test: dict,
    bench: dict,
    cache_path: str = "docs/last_report.txt"
) -> str:

    report = explain_strategy(
        rules,
        metrics_train,
        metrics_test,
        bench
    )

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report


if __name__ == "__main__":

    fake_train = {
        "CAGR": 0.18,
        "sharpe": 1.2,
        "sortino": 1.6,
        "calmar": 0.82,
        "max_drawdown": -0.22,
        "win_rate": 0.55,
        "exposure": 0.62
    }

    fake_test = {
        "CAGR": 0.09,
        "sharpe": 0.6,
        "sortino": 0.8,
        "calmar": 0.30,
        "max_drawdown": -0.30,
        "win_rate": 0.49,
        "exposure": 0.58
    }

    fake_bench = {
        "CAGR": 0.25,
        "sharpe": 0.9,
        "sortino": 1.1,
        "calmar": 0.55,
        "max_drawdown": -0.45
    }

    rules = """
    TrendGuard uses a fast EMA and slow EMA.

    Entry:
    - Fast EMA crosses above slow EMA.
    - Current price must also be above the slow EMA.

    Exit:
    - Fast EMA crosses below slow EMA, OR
    - Price falls below the highest price since entry minus
      ATR multiplier times ATR.

    The strategy is long-only.
    It does not short.
    It does not use leverage.
    """

    report = explain_strategy_cached(
        rules,
        fake_train,
        fake_test,
        fake_bench
    )

    print("\n--- AI REPORT ---\n")
    print(report)
