# Applied Analysis

Applied Analysis is a collection of small, practical analytical examples.

The purpose is simple: take a dataset, identify what is changing, extract a useful signal, and explain what that signal means in plain language.

This is not a general analytics toolkit or a folder of calculators. Each project should help someone understand what matters in the data and why it may be useful for a decision.

## Core Pattern

Every example in this repository should follow the same basic pattern:

1. **Data**: start with a simple, real or representative dataset
2. **Change**: identify movement over time or differences across conditions
3. **Signal**: extract the main thing worth noticing
4. **Interpretation**: explain what the signal means in plain language

In short:

```text
data -> change -> signal -> interpretation
```

The interpretation is the point. Calculations support the analysis, but they are not the final product.

## Repository Structure

```text
applied-analysis/
  README.md
  requirements.txt
  examples/
    trend_signal/
    kidney_transplant_signal_comparison/
    agriculture_system_pressure_africa/
  src/
```

- `examples/` contains one small project per folder.
- `examples/trend_signal/` is the first example and shows the core pattern.
- `examples/kidney_transplant_signal_comparison/` is the comparison example and shows how two public system signals can be interpreted together.
- `examples/agriculture_system_pressure_africa/` extends the pattern into threshold detection with an Africa-focused agricultural systems example.
- `examples/ssa_agricultural_capital_pressure/` adds contextual events and capital-cost context on top of threshold windows for Sub-Saharan Africa.
- `src/` is reserved for simple reusable components once multiple examples need them.

## First Example: Trend Signal

`examples/trend_signal/` asks a simple question:

What is changing over time, and what should we notice?

It uses a small extract of the FRED 10-year Treasury rate series, compares the first and last values, classifies the movement, prints a short interpretation, and saves a simple chart.

Start here: [Trend Signal Example](./examples/trend_signal/)

For the plain-language analysis, see [Trend Signal Insight](./examples/trend_signal/INSIGHT.md).

## Second Example: Kidney Transplant Signal Comparison

`examples/kidney_transplant_signal_comparison/` asks:

How does kidney transplant volume relate to kidney transplant waitlist demand over time?

It compares annual kidney transplants with annual kidney waitlist additions from public OPTN reporting, summarizes whether the two signals are moving together or apart, checks for a simple lag pattern, and explains the result in plain language.

Run it with:

```bash
python3 -m pip install -r requirements.txt
python3 examples/kidney_transplant_signal_comparison/kidney_transplant_signal_comparison.py
```

## Third Example: Agriculture System Pressure in Africa

`examples/agriculture_system_pressure_africa/` asks:

When does imported food become a large enough share of a regional food system to merit closer attention?

It aligns Sub-Saharan Africa agriculture value added with estimated food imports, calculates an imported-share proxy, detects threshold crossings, and explains the result in plain language.

Run it with:

```bash
python3 -m pip install -r requirements.txt
python3 examples/agriculture_system_pressure_africa/agriculture_system_pressure_africa.py
```

## Fourth Example: SSA Agricultural Capital Pressure

`examples/ssa_agricultural_capital_pressure/` asks:

When a system enters an imported-food pressure window, what contextual events and capital-cost conditions may help explain what was happening around that period?

It reuses the Sub-Saharan Africa agriculture threshold dataset, adds a small curated events file, overlays those events on the threshold windows, and adds a transparent capital-cost proxy to deepen the interpretation without claiming causation.

Run it with:

```bash
python3 -m pip install -r requirements.txt
python3 examples/ssa_agricultural_capital_pressure/ssa_agricultural_capital_pressure.py
```

## Future Direction

The early goal is to build a small set of examples that translate data into useful interpretations.

As the examples grow, selected projects can be surfaced through a unified UI and hosted publicly. The focus should remain on clear signals, plain-language interpretation, and minimal setup.

This repository will expand with additional examples focused on:
- comparing signals
- identifying thresholds and inflection points
- adding context to data
- translating analysis into decision-oriented summaries

## Contributing Ideas

If there is a signal or real-world question you’d like to see explored, feel free to open an issue.

The goal is to build examples that focus on:
- what is changing
- what matters
- how to interpret it clearly

Not all ideas will be implemented, but thoughtful suggestions are welcome.
