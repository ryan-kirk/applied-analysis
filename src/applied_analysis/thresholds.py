from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar


Position = TypeVar("Position")


@dataclass(frozen=True)
class ThresholdCrossing(Generic[Position]):
    position: Position
    value: float
    crossed_above: bool

    @property
    def direction(self):
        return "up" if self.crossed_above else "down"


@dataclass(frozen=True)
class ThresholdRun(Generic[Position]):
    start: Position
    end: Position
    duration: int
    peak_value: float


def _is_above_threshold(value, threshold, inclusive):
    if inclusive:
        return value >= threshold
    return value > threshold


def detect_threshold_runs(points: Sequence[tuple[Position, float]], threshold: float, *, inclusive: bool = True):
    if not points:
        return [], []

    crossings = []
    runs = []
    previous_position, previous_value = points[0]
    previous_state = _is_above_threshold(previous_value, threshold, inclusive)
    run_start = previous_position if previous_state else None
    run_peak = previous_value if previous_state else None
    run_length = 1 if previous_state else 0

    for position, value in points[1:]:
        current_state = _is_above_threshold(value, threshold, inclusive)

        if current_state != previous_state:
            crossings.append(
                ThresholdCrossing(
                    position=position,
                    value=value,
                    crossed_above=current_state,
                )
            )

            if current_state:
                run_start = position
                run_peak = value
                run_length = 1
            else:
                runs.append(
                    ThresholdRun(
                        start=run_start,
                        end=previous_position,
                        duration=run_length,
                        peak_value=run_peak,
                    )
                )
                run_start = None
                run_peak = None
                run_length = 0

        elif current_state and run_peak is not None:
            run_peak = max(run_peak, value)
            run_length += 1

        previous_state = current_state
        previous_position = position

    if previous_state and run_start is not None and run_peak is not None:
        runs.append(
            ThresholdRun(
                start=run_start,
                end=previous_position,
                duration=run_length,
                peak_value=run_peak,
            )
        )

    return crossings, runs


def format_duration(count: int, unit: str = "year"):
    suffix = unit if count == 1 else f"{unit}s"
    return f"{count} {suffix}"