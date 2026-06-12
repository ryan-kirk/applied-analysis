---
title: Applied Analysis
category_label: Analytics Portfolio
summary: Decision-oriented analytical case studies and reusable Python components for identifying changes, thresholds, and operational pressure in real-world systems.
repo_url: https://github.com/ryan-kirk/applied-analysis
order: 10
comments: false
---

Applied Analysis is a portfolio repository built around a simple pattern: take a dataset, identify what is changing, extract the useful signal, and explain why that signal matters in plain language.

## What It Does

The repository combines public-facing analytical examples with lightweight reusable Python components. Each example is designed to move beyond raw charts into a decision-support interpretation.

Current capabilities include:

- directional trend analysis
- signal comparison across related series
- threshold detection
- contextual event overlays
- multi-signal consistency analysis
- plain-language summaries that connect the math to the decision

## How It Is Structured

- `examples/` contains the example analyses, source data, output images, and insight write-ups
- `src/applied_analysis/` contains reusable analytical components shared across examples
- `docs/` contains the GitHub Pages portfolio and case-study layer
- `tests/` covers the shared analytical logic

## Why It Matters

This repository shows a style of work that is useful in consulting, applied research, and product strategy settings: make a complex system easier to reason about without hiding the mechanics. The examples are intentionally compact, but they demonstrate how to frame a question, build a transparent analytical method, and communicate the result clearly.

## Representative Use Cases

- translating a noisy time series into a practical directional signal
- comparing supply and demand indicators within constrained systems
- detecting when a system crosses from normal variation into meaningful pressure
- layering domain events onto quantitative signals to improve interpretation
- turning analytical outputs into shareable public case studies

## Repository Links

- [Source repository](https://github.com/ryan-kirk/applied-analysis)
- [Homepage]({{ '/' | relative_url }})
- [Project list]({{ '/projects/' | relative_url }})
