---
title: When Cheap Tokens Get Expensive: The Hidden Cost of Agentic Workflows
comments: true
excerpt: Falling token prices can make unit inference cheaper while agentic workflows still become more token-hungry. This post explains the conflict between lower list prices and higher orchestration-driven token usage.
---

![Four-panel chart showing token list prices, token usage per task, orchestration inflation, net task cost after cache, and event overlays]({{ '/assets/images/token-economics-orchestration.png' | relative_url }})

Falling token prices are real. But lower unit prices do not automatically mean AI work gets proportionally cheaper once workflows become multi-step, retrieval-heavy, and loop-driven.

The token economics example in Applied Analysis was built to answer a simple question:

Are falling token prices reducing cost per task, or are agents and orchestration increasing token usage enough to offset the savings?

## The Two Signals

The analysis compares two signals that become more useful when read together than separately:

- estimated blended token list price per million tokens
- estimated workflow token usage per task

If both fall, the workflow is getting cheaper and lighter. If both rise, richer workflows are also getting more expensive. But if prices fall while usage rises, the signals conflict. That is the case in this example.

The unit economics improve. The workflow economics improve more slowly.

## What the Example Shows

In this scenario, estimated blended token list prices decline sharply across the period while estimated workflow token usage per task rises materially. That means the market is getting cheaper at the token level even as agentic patterns push more tokens through each completed task.

The effect is not trivial. Planner, retriever, tool, executor, and critic loops do not just add a small amount of extra prompt context. They can multiply total token demand relative to a simpler single-pass baseline.

## Thresholds That Matter

Three thresholds help translate that movement into plain language:

- estimated orchestration inflation factor >= 3.0
- estimated cached discount ratio >= 0.80
- estimated net workflow cost per task decline >= 50% versus the 2023 baseline

The most important threshold is orchestration inflation. Once estimated workflow tokens rise above three times a simpler baseline, the workload looks less like a richer prompt and more like a structurally heavier execution system.

The cache threshold matters for a different reason. Repeated context only becomes meaningfully cheaper if enough of that repeated input is actually treated as cached-discounted input.

The cost-decline threshold asks whether lower list prices still win overall at the task level.

## Interpreting the Conflict

The useful takeaway is not that cheap tokens make AI expensive. It is more specific than that.

Lower list prices can still reduce net cost per task, while orchestration inflation absorbs a meaningful share of those savings. In other words, the workflow can get cheaper and more token-hungry at the same time.

That is the kind of mixed systems signal that gets lost if price is read without usage, or usage is read without price.

## Data and Method Notes

This example uses a mix of public and scenario-based inputs:

- `vendor_model_pricing.csv`: public pricing anchors from vendor pricing pages
- `task_token_profiles.csv`: estimated task token profiles for support, research, coding, and heavier orchestration work
- `orchestration_patterns.csv`: estimated workflow patterns such as direct prompting, retrieval-assisted work, and planner-critic loops
- `token_market_events.csv`: public milestone events used as descriptive context on the chart

The pricing anchors are public. The task and orchestration profiles are synthetic scenario assumptions. They are intended to construct useful signals, not to claim proprietary vendor telemetry or exact production usage behavior.

## Read the Full Example

The full example, chart, and source data live in the repository:

- [Token economics example](https://github.com/ryan-kirk/applied-analysis/tree/main/examples/token_economics_orchestration)
- [Insight document](https://github.com/ryan-kirk/applied-analysis/blob/main/examples/token_economics_orchestration/INSIGHT.md)