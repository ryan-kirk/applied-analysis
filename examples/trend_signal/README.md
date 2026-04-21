# Trend Signal

This first example shows the core Applied Analysis pattern:

```text
data -> change -> signal -> interpretation
```

## Question

What is changing over time, and what should we notice?

## What It Does

- starts with a small representative time series
- compares the first and last values
- classifies the movement as stable, moderate, or meaningful
- prints a plain-language interpretation

## Why It Matters

Many tools show values.

This example turns values into a signal someone can understand and use.

## How To Run

From the repository root:

```bash
python3 examples/trend_signal/trend_signal.py
```
