import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calculate_analytics import calculate
from render_readme_cards import render_heatmap, render_monthly, render_overview, render_repositories, render_streak


class RenderingTests(unittest.TestCase):
    def test_cards_are_deterministic_well_formed_and_dimensioned(self):
        data = [{"date": "2026-11-09", "contributionCount": 3}]
        analytics = calculate(data, date(2026, 11, 10))
        cards = [render_overview(analytics), render_heatmap(analytics), render_monthly(analytics),
                 render_streak(analytics), render_repositories([])]
        again = [render_overview(analytics), render_heatmap(analytics), render_monthly(analytics),
                 render_streak(analytics), render_repositories([])]
        self.assertEqual(cards, again)
        for card in cards:
            root = ET.fromstring(card)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertFalse(root.findall(".//{http://www.w3.org/2000/svg}animate"))

    def test_heatmap_tooltips_include_date_count_and_level(self):
        analytics = calculate([{"date": "2026-11-09", "contributionCount": 7}], date(2026, 11, 10))
        card = render_heatmap(analytics)
        self.assertIn("2026-11-09: 7 contributions · level 3", card)


if __name__ == "__main__":
    unittest.main()
