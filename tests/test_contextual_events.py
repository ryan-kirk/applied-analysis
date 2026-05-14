import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applied_analysis.contextual_events import (
    ContextEvent,
    build_context_windows,
    match_events_to_windows,
)
from applied_analysis.thresholds import ThresholdRun


class ContextualEventsTests(unittest.TestCase):
    def test_builds_named_context_windows_from_threshold_runs(self):
        runs = [
            ThresholdRun(start=2011, end=2014, duration=4, peak_value=0.19),
            ThresholdRun(start=2016, end=2018, duration=3, peak_value=0.16),
        ]

        windows = build_context_windows(runs, prefix="Pressure window")

        self.assertEqual(
            [(item.name, item.start, item.end, item.duration) for item in windows],
            [("Pressure window 1", 2011, 2014, 4), ("Pressure window 2", 2016, 2018, 3)],
        )

    def test_matches_events_before_during_and_after_windows(self):
        windows = build_context_windows(
            [ThresholdRun(start=2011, end=2014, duration=4, peak_value=0.19)],
            prefix="Pressure window",
        )
        events = [
            ContextEvent(2010, "precursor", "Precursor", "A year before", ""),
            ContextEvent(2012, "during", "Within", "During the window", ""),
            ContextEvent(2015, "after", "Aftermath", "A year after", ""),
            ContextEvent(2008, "outside", "Outside", "Outside scope", ""),
        ]

        matches = match_events_to_windows(events, windows, years_before=1, years_after=1)

        self.assertEqual(
            [(item.event.event_name, item.timing, item.offset_years) for item in matches],
            [("Precursor", "before", 1), ("Within", "during", 1), ("Aftermath", "after", 1)],
        )


if __name__ == "__main__":
    unittest.main()