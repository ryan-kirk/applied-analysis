from collections.abc import Sequence


def classify_trend_direction(series: Sequence[float], tolerance: float = 0.05) -> str:
    if len(series) < 2:
        return "stable"

    start = float(series[0])
    end = float(series[-1])

    if start == 0:
        absolute_change = end - start
        if abs(absolute_change) <= tolerance:
            return "stable"
        return "increasing" if absolute_change > 0 else "decreasing"

    relative_change = (end - start) / abs(start)
    if abs(relative_change) <= tolerance:
        return "stable"
    return "increasing" if relative_change > 0 else "decreasing"


def compare_signal_directions(
    signal_a_direction: str,
    signal_b_direction: str,
    signal_a_name: str,
    signal_b_name: str,
) -> dict[str, str]:
    normalized_a = signal_a_direction.strip().lower()
    normalized_b = signal_b_direction.strip().lower()

    if normalized_a == normalized_b:
        if normalized_a == "stable":
            relationship = "mixed conditions"
            explanation = (
                f"{signal_a_name} and {signal_b_name} are both broadly stable, so the pair does not point to a clear directional shift."
            )
        else:
            relationship = "same direction"
            explanation = (
                f"{signal_a_name} and {signal_b_name} are both {normalized_a}, so the signals point in the same direction."
            )
    elif "stable" in {normalized_a, normalized_b}:
        relationship = "mixed conditions"
        explanation = (
            f"{signal_a_name} is {normalized_a} while {signal_b_name} is {normalized_b}, which suggests a mixed backdrop rather than a clean agreement."
        )
    else:
        relationship = "conflict"
        explanation = (
            f"{signal_a_name} is {normalized_a} while {signal_b_name} is {normalized_b}, so the signals conflict."
        )

    return {
        "relationship": relationship,
        "signal_a_direction": normalized_a,
        "signal_b_direction": normalized_b,
        "explanation": explanation,
    }


def compare_trend_consistency(
    signal_growth_rates: dict[str, float],
    *,
    demand_signal: str | None = None,
    stable_tolerance: float = 0.05,
    pressure_gap: float = 0.25,
    bottleneck_gap: float = 0.50,
) -> dict[str, object]:
    if not signal_growth_rates:
        return {
            "classification": "insufficient data",
            "consistency_score": 0.0,
            "strongest_constraint": None,
            "aligned_signals": [],
            "lagging_signals": [],
            "signal_directions": {},
            "growth_gaps": {},
            "reference_signal": demand_signal,
        }

    signal_directions = {
        name: classify_trend_direction([1.0, 1.0 + growth], tolerance=stable_tolerance)
        for name, growth in signal_growth_rates.items()
    }

    reference_signal = demand_signal or max(
        signal_growth_rates,
        key=lambda name: abs(signal_growth_rates[name]),
    )
    reference_growth = signal_growth_rates[reference_signal]
    reference_direction = signal_directions[reference_signal]

    aligned_signals = []
    lagging_signals = []
    growth_gaps = {}
    positive_gaps = []

    for signal_name, growth_rate in signal_growth_rates.items():
        if signal_name == reference_signal:
            continue

        gap = reference_growth - growth_rate
        growth_gaps[signal_name] = gap

        if reference_direction == signal_directions[signal_name] or "stable" in {
            reference_direction,
            signal_directions[signal_name],
        }:
            aligned_signals.append(signal_name)
        else:
            lagging_signals.append(signal_name)

        if gap > 0:
            positive_gaps.append((signal_name, gap))
            if gap - pressure_gap > 1e-9:
                lagging_signals.append(signal_name)

    lagging_signals = sorted(set(lagging_signals))
    aligned_signals = sorted(
        signal_name for signal_name in set(aligned_signals) if signal_name not in lagging_signals
    )

    if positive_gaps:
        strongest_constraint, strongest_gap = max(positive_gaps, key=lambda item: item[1])
    else:
        strongest_constraint = None
        strongest_gap = 0.0

    if abs(reference_growth) <= stable_tolerance:
        consistency_score = 1.0 if not lagging_signals else 0.5
    else:
        normalized_gaps = [
            min(abs(gap) / abs(reference_growth), 1.0)
            for gap in growth_gaps.values()
        ]
        consistency_score = max(0.0, 1.0 - (sum(normalized_gaps) / max(len(normalized_gaps), 1)))

    if strongest_gap >= bottleneck_gap:
        classification = "diverging"
    elif lagging_signals:
        classification = "pressured"
    else:
        classification = "consistent"
        strongest_constraint = None

    return {
        "classification": classification,
        "consistency_score": round(consistency_score, 4),
        "strongest_constraint": strongest_constraint,
        "aligned_signals": aligned_signals,
        "lagging_signals": lagging_signals,
        "signal_directions": signal_directions,
        "growth_gaps": growth_gaps,
        "reference_signal": reference_signal,
        "reference_direction": reference_direction,
    }