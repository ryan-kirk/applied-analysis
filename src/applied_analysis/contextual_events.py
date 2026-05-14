from csv import DictReader
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .thresholds import ThresholdRun


@dataclass(frozen=True)
class ContextWindow:
    name: str
    start: int
    end: int
    duration: int
    peak_value: float


@dataclass(frozen=True)
class ContextEvent:
    year: int
    event_type: str
    event_name: str
    description: str
    source_url: str


@dataclass(frozen=True)
class WindowEventMatch:
    window_name: str
    window_start: int
    window_end: int
    event: ContextEvent
    timing: str
    offset_years: int


def load_context_events(path: Path) -> list[ContextEvent]:
    with path.open(newline="", encoding="utf-8") as file:
        return [
            ContextEvent(
                year=int(row["year"]),
                event_type=row["event_type"].strip(),
                event_name=row["event_name"].strip(),
                description=row["description"].strip(),
                source_url=row.get("source_url", "").strip(),
            )
            for row in DictReader(file)
        ]


def build_context_windows(
    runs: Sequence[ThresholdRun[int]],
    *,
    prefix: str = "Context window",
) -> list[ContextWindow]:
    return [
        ContextWindow(
            name=f"{prefix} {index}",
            start=run.start,
            end=run.end,
            duration=run.duration,
            peak_value=run.peak_value,
        )
        for index, run in enumerate(runs, start=1)
    ]


def match_events_to_windows(
    events: Iterable[ContextEvent],
    windows: Sequence[ContextWindow],
    *,
    years_before: int = 1,
    years_after: int = 0,
) -> list[WindowEventMatch]:
    matches: list[WindowEventMatch] = []

    for window in windows:
        for event in events:
            if window.start <= event.year <= window.end:
                matches.append(
                    WindowEventMatch(
                        window_name=window.name,
                        window_start=window.start,
                        window_end=window.end,
                        event=event,
                        timing="during",
                        offset_years=event.year - window.start,
                    )
                )
            elif window.start - years_before <= event.year < window.start:
                matches.append(
                    WindowEventMatch(
                        window_name=window.name,
                        window_start=window.start,
                        window_end=window.end,
                        event=event,
                        timing="before",
                        offset_years=window.start - event.year,
                    )
                )
            elif window.end < event.year <= window.end + years_after:
                matches.append(
                    WindowEventMatch(
                        window_name=window.name,
                        window_start=window.start,
                        window_end=window.end,
                        event=event,
                        timing="after",
                        offset_years=event.year - window.end,
                    )
                )

    return sorted(matches, key=lambda item: (item.window_start, item.event.year, item.event.event_name))