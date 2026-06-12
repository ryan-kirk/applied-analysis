# AI Compute, Memory, Storage, and Power: Can Infrastructure Keep Up?

This example extends Applied Analysis into multi-signal infrastructure consistency analysis.

```text
data -> comparison -> thresholds -> context -> interpretation
```

## Question

Can AI infrastructure keep up with growing AI demand?

More specifically:

- is AI demand rising faster than the infrastructure needed to support it?
- which resources appear most constrained?
- do the signals tell a consistent story, or do they begin to diverge?

## Framing

This is a public, educational infrastructure analysis.

It does not claim proprietary capacity numbers or attempt to forecast the AI market. Instead, it uses transparent indexed signals informed by public sources so the comparison stays legible across compute, memory, storage, and power.

## What It Does

- loads a local indexed dataset for AI demand and infrastructure supply signals
- classifies the long-run direction of each signal
- compares demand with aggregate infrastructure direction
- computes yearly growth gaps between demand and each resource
- applies reusable trend consistency analysis across all signals
- detects resource pressure, bottleneck, and divergence windows
- overlays major AI infrastructure events for context
- saves a four-panel chart, yearly summary CSV, and a console report

## New Reusable Capability

This example adds a reusable helper to the core library:

- `compare_trend_consistency()`

That helper supports higher-level divergence analysis by checking whether multiple signals move in ways that appear internally consistent and by identifying the strongest constraint when they do not.

## Data

The example uses two local CSV files:

- `data/ai_infrastructure_signals.csv`
- `data/ai_infrastructure_events.csv`

The values are indexed to a common 2020 baseline so different units can be compared transparently on the same chart. Source labels point to public reports or disclosures that informed the relative signal design.

## Thresholds

The script checks three thresholds:

- resource pressure window: demand growth exceeds a resource growth rate by more than 25 percentage points
- potential constraint: demand growth exceeds a resource growth rate by more than 50 percentage points
- system divergence window: consistency score falls below `0.60`

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/ai_compute_constraints/ai_compute_constraints.py
```

## Outputs

The script creates these files in `outputs/`:

- `ai_compute_constraints.png`
- `ai_compute_constraints_summary.csv`

## Takeaway

The point is not that AI infrastructure is failing. The point is that demand, compute, memory, storage, and power can all move in the same broad direction while still creating practical constraint windows because they are not scaling at the same rate.