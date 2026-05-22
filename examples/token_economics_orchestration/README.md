# Token Economics, Task Types, and Orchestration Inflation

This example extends Applied Analysis into AI token economics using a lightweight, public, educational framing.

```text
data -> comparison -> thresholds -> context -> interpretation
```

## Question

Are falling token prices reducing cost per task, or are agents and orchestration increasing token usage enough to offset the savings?

## Framing

This is not vendor-internal usage analysis and it is not a market forecast.

The example combines:

- public model pricing references where available
- transparent scenario assumptions for task token usage
- transparent scenario assumptions for orchestration overhead and cache reuse

The goal is to construct useful signals, not to claim exact proprietary consumption behavior.

## Signals Compared

The example compares two related signals over time:

1. blended token list price trend
2. weighted token usage per task, shaped by task mix and orchestration patterns

It then checks whether lower list prices are being offset by heavier token usage from multi-step agent workflows.

## Local Data

The example uses four small local CSV files:

- `data/vendor_model_pricing.csv`
- `data/task_token_profiles.csv`
- `data/orchestration_patterns.csv`
- `data/token_market_events.csv`

Task and orchestration usage values are scenario assumptions. Pricing rows point to public pricing pages and are treated as representative list-price anchors for each period.

## What It Does

- classifies token price direction and token usage direction
- compares whether the two signals move together, conflict, or imply mixed conditions
- computes orchestration inflation as total task tokens relative to a simpler baseline
- estimates gross cost per task and net cost per task after cache reuse
- detects threshold windows for orchestration inflation, cache efficiency, and cost decline
- overlays curated market events on a four-panel chart
- writes reusable scenario outputs and a compact summary CSV

## Thresholds

The script checks for three threshold conditions:

- orchestration inflation factor `>= 3.0`
- cached discount ratio `>= 0.80`
- cost per task decline versus the first year `>= 0.50`

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/token_economics_orchestration/token_economics_orchestration.py
```

## Outputs

The script creates these files in `outputs/`:

- `token_cost_scenarios.csv`
- `token_economics_orchestration.png`
- `token_economics_summary.csv`

## Recommended Title

**When Cheap Tokens Get Expensive: The Hidden Cost of Agentic Workflows**