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