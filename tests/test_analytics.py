import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from calculate_analytics import calculate


def item(day, count):
    return {"date": day, "contributionCount": count}


class AnalyticsTests(unittest.TestCase):
    def test_streak_uses_consecutive_calendar_dates_and_yesterday_when_today_empty(self):
        result = calculate([item("2026-11-08", 1), item("2026-11-09", 1), item("2026-11-10", 0)], date(2026, 11, 10))
        self.assertEqual(result["current_streak"], 2)

    def test_missing_calendar_date_breaks_streak(self):
        result = calculate([item("2026-11-07", 1), item("2026-11-09", 2), item("2026-11-10", 1)], date(2026, 11, 10))
        self.assertEqual(result["current_streak"], 2)

    def test_month_totals_and_partial_month(self):
        result = calculate([item("2026-11-01", 2), item("2026-11-02", 4)], date(2026, 11, 2))
        self.assertEqual(result["months"][-1]["total"], 6)
        self.assertTrue(result["months"][-1]["incomplete"])
        self.assertEqual(result["months"][-1]["active_days"], 2)

    def test_longest_streak_can_precede_display_window(self):
        days = [item(f"2025-10-{d:02d}", 1) for d in range(1, 8)]
        result = calculate(days, date(2026, 11, 10))
        self.assertEqual(result["longest_streak"], 7)


if __name__ == "__main__":
    unittest.main()
