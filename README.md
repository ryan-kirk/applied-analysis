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

## What Belongs Here

Good examples are small, clear, and focused. They should answer questions like:

- What changed?
- Is the change meaningful?
- What should someone notice?
- How might this affect a decision?

Each example should be easy for a non-specialist to read, run, and understand.

## Repository Structure

```text
applied-analysis/
  README.md
  STRATEGY.md
  requirements.txt
  examples/
    trend_signal/
  src/
```

- `examples/` contains one small project per folder.
- `examples/trend_signal/` is the first example and shows the core pattern.
- `src/` is reserved for simple reusable components once multiple examples need them.
- `STRATEGY.md` describes the short- and long-term direction for the repository.

## First Example

`examples/trend_signal/` asks:

> What is changing over time, and what should we notice?

It uses a small time series, compares the first and last values, classifies the movement, and prints a short interpretation.

Run it with:

```bash
python3 examples/trend_signal/trend_signal.py
```

## Direction

The early goal is to build a small set of credible examples that translate data into useful interpretations.

As the examples grow, selected projects can be surfaced through a unified UI and hosted publicly on Fly. The priority should remain the same: clear signals, plain-language interpretation, and minimal setup.
