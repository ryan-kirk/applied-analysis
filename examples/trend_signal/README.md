# Trend Signal

This example shows how a real-world time series can be translated into a simple signal and plain-language interpretation.

```text
data -> change -> signal -> interpretation
```

## Question

What is changing over time, and what should we notice?

## Dataset

The example uses a small local CSV of the US 10-year Treasury rate.

The data is based on the FRED `DGS10` series:

> Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity

Source: https://fred.stlouisfed.org/series/DGS10

To keep the example simple and reproducible, a small representative extract is stored locally in `data/us_10_year_treasury_rate.csv`. The script does not call FRED or depend on any external service at runtime.

## What It Does

- loads a small CSV with `date` and `value`
- compares the first and last values
- computes the point change and relative percent change
- calculates a simple average yearly movement
- labels the signal as increasing, decreasing, or stable
- prints a plain-language interpretation
- saves a shareable text summary
- saves a simple line chart

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/trend_signal/trend_signal.py
```

## Outputs

The script prints a clean console summary and creates two files in this folder:

- `trend_signal_summary.txt`
- `trend_signal.png`
