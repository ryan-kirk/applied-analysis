import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applied_analysis.signal_comparison import (
    classify_trend_direction,
    compare_signal_directions,
)


class SignalComparisonTests(unittest.TestCase):
    def test_classifies_increasing_series(self):
        self.assertEqual(classify_trend_direction([10, 11, 13]), "increasing")

    def test_classifies_decreasing_series(self):
        self.assertEqual(classify_trend_direction([100, 90, 70]), "decreasing")

    def test_classifies_stable_series_within_tolerance(self):
        self.assertEqual(classify_trend_direction([100, 102, 104], tolerance=0.05), "stable")

    def test_treats_small_absolute_move_from_zero_as_stable(self):
        self.assertEqual(classify_trend_direction([0, 0.02], tolerance=0.05), "stable")

    def test_labels_same_direction(self):
        result = compare_signal_directions(
            "decreasing",
            "decreasing",
            "Token cost per million",
            "Net cost per task",
        )

        self.assertEqual(result["relationship"], "same direction")
        self.assertIn("same direction", result["explanation"])

    def test_labels_conflict(self):
        result = compare_signal_directions(
            "decreasing",
            "increasing",
            "Token cost per million",
            "Token usage per task",
        )

        self.assertEqual(result["relationship"], "conflict")

    def test_labels_mixed_conditions_when_one_signal_is_stable(self):
        result = compare_signal_directions(
            "stable",
            "increasing",
            "Token cost per million",
            "Token usage per task",
        )

        self.assertEqual(result["relationship"], "mixed conditions")


if __name__ == "__main__":
    unittest.main()