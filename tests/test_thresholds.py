import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applied_analysis.thresholds import detect_threshold_runs, format_duration


class ThresholdDetectionTests(unittest.TestCase):
    def test_detects_crossings_and_runs(self):
        points = [
            (2000, 0.10),
            (2001, 0.12),
            (2002, 0.16),
            (2003, 0.18),
            (2004, 0.14),
            (2005, 0.17),
        ]

        crossings, runs = detect_threshold_runs(points, 0.15)

        self.assertEqual([(item.position, item.direction) for item in crossings], [(2002, "up"), (2004, "down"), (2005, "up")])
        self.assertEqual([(item.start, item.end, item.duration) for item in runs], [(2002, 2003, 2), (2005, 2005, 1)])

    def test_treats_exact_threshold_as_crossed_when_inclusive(self):
        crossings, runs = detect_threshold_runs([(1, 0.14), (2, 0.15), (3, 0.15)], 0.15)

        self.assertEqual(len(crossings), 1)
        self.assertTrue(crossings[0].crossed_above)
        self.assertEqual(runs[0].duration, 2)

    def test_handles_empty_input(self):
        crossings, runs = detect_threshold_runs([], 0.15)

        self.assertEqual(crossings, [])
        self.assertEqual(runs, [])

    def test_supports_non_numeric_positions(self):
        crossings, runs = detect_threshold_runs([("a", 0.10), ("b", 0.20), ("c", 0.22), ("d", 0.12)], 0.15)

        self.assertEqual([(item.position, item.direction) for item in crossings], [("b", "up"), ("d", "down")])
        self.assertEqual([(item.start, item.end, item.duration) for item in runs], [("b", "c", 2)])

    def test_formats_duration(self):
        self.assertEqual(format_duration(1), "1 year")
        self.assertEqual(format_duration(3), "3 years")


if __name__ == "__main__":
    unittest.main()