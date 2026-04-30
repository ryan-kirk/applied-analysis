# Kidney Transplant Signal Comparison

This example adapts the repository's basic signal-comparison pattern to a public-interest healthcare systems question.

```text
data -> comparison -> signal -> interpretation
```

## Question

How does kidney transplant volume relate to kidney transplant waitlist demand over time?

## Framing

This is a public-interest systems analysis.

It is not medical advice, not patient-specific analysis, and not a clinical prediction tool. The goal is to compare two public system signals and explain what they suggest in plain language.

## Dataset

The local dataset in `data/kidney_transplant_system_signals.csv` contains annual U.S. kidney transplant system counts for 2016 through 2025.

Signals used:

- `kidney_transplants`: annual kidney transplants performed
- `kidney_waitlist_additions`: annual kidney waitlist additions

Source basis:

- OPTN Metrics dashboard: `https://insights.unos.org/OPTN-metrics/`
- HRSA OPTN Data & Calculators page: `https://www.hrsa.gov/optn/data`

Why waitlist additions?

The original question points toward waitlist demand. In this small public example, annual kidney waitlist additions are used as a transparent demand proxy because they are available from the public OPTN metrics dashboard in a way that is easy to extract and store locally.

## What It Does

- loads a small local CSV with annual kidney transplant system signals
- compares transplant volume with waitlist demand flow
- labels the relationship as moving together, moving apart, or mixed
- checks for a simple possible one-year lag
- prints a plain-language interpretation
- saves a two-line chart
- saves a shareable text summary

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/kidney_transplant_signal_comparison/kidney_transplant_signal_comparison.py
```

## Outputs

The script prints a console summary and creates two files in this folder:

- `kidney_transplant_signal_comparison_summary.txt`
- `kidney_transplant_signal_comparison.png`