"""Protect counting semantics, missingness, and code-based geography."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze_daytime_visits import build_pair_month, summarize_pairs


class DaytimeVisitTests(unittest.TestCase):
    def setUp(self):
        self.areas = pd.DataFrame({"kapanewon_code": ["a", "b", "c"],
                                   "kapanewon": ["JETIS", "JETIS", "TUJUAN"],
                                   "kab_kota": ["BANTUL", "YOGYAKARTA", "YOGYAKARTA"]})
        self.months = ["2021-12", "2022-01", "2022-02"]
        self.homes = pd.DataFrame({"month": self.months, "origin_code": "a", "n_homed_maids": [100, 1000, 100]})
        self.od = pd.DataFrame({"month": self.months, "origin_code": "a", "dest_code": "b",
                                "n_maids": [10, 200, 10], "n_homed_maids": [100, 1000, 100]})

    def build(self, od=None):
        return build_pair_month(self.od if od is None else od, self.homes, self.areas, self.months)

    def test_jetis_codes_retained(self):
        pairs = self.build()
        self.assertEqual(int(pairs.published.sum()), 3)
        self.assertTrue(pairs.loc[pairs.published, "origin_kapanewon"].eq("JETIS").all())
        self.assertTrue(pairs.loc[pairs.published, "dest_kapanewon"].eq("JETIS").all())

    def test_missing_month_is_unknown_and_excluded_from_primary_ranking(self):
        pairs = self.build(self.od.iloc[:2])
        feb = pairs[(pairs.dest_code == "b") & (pairs.month == "2022-02")].iloc[0]
        self.assertTrue(pd.isna(feb.n_maids))
        self.assertTrue(pd.isna(feb.visit_rate))
        summary = summarize_pairs(pairs).query("dest_code == 'b'").iloc[0]
        self.assertEqual(summary.months_published, 2)
        self.assertTrue(pd.isna(summary.mean_devices_per_month))
        self.assertTrue(pd.isna(summary.pooled_visit_rate))

    def test_rate_pools_counts_not_unweighted_monthly_rates(self):
        row = summarize_pairs(self.build()).query("dest_code == 'b'").iloc[0]
        self.assertAlmostEqual(row.pooled_visit_rate, 220 / 1200)
        self.assertNotAlmostEqual(row.pooled_visit_rate, (0.1 + 0.2 + 0.1) / 3)

    def test_never_published_pair_stays_null(self):
        row = summarize_pairs(self.build()).query("dest_code == 'c'").iloc[0]
        self.assertEqual(row.months_published, 0)
        self.assertTrue(pd.isna(row.observed_device_months))

    def test_denominator_mismatch_is_rejected(self):
        broken = self.od.copy()
        broken.loc[0, "n_homed_maids"] = 999
        with self.assertRaisesRegex(ValueError, "disagree"):
            self.build(broken)

    def test_duplicate_input_pair_month_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.build(pd.concat([self.od, self.od.iloc[:1]], ignore_index=True))


if __name__ == "__main__":
    unittest.main()
