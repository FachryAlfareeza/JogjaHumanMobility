"""Legacy dashboard comparisons preserve unpublished OD values as unknown."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from applied import city_visits, complete_pair_rates


class AppliedVisitTests(unittest.TestCase):
    def test_incomplete_panjatan_sedayu_comparison_stays_unknown(self):
        pairs = pd.DataFrame({"month": ["2022-01", "2022-02"],
                              "dest_code": "34.02.17", "visit_rate": [14 / 205, 7 / 180]})
        rate = complete_pair_rates(pairs, "dest_code", ["2021-12", "2022-01", "2022-02"])
        self.assertTrue(pd.isna(rate.loc["34.02.17"]))

    def test_complete_rates_keep_equal_month_weight(self):
        pairs = pd.DataFrame({"month": ["2021-12", "2022-01", "2022-02"],
                              "dest_code": "d", "visit_rate": [.1, .2, .3]})
        rate = complete_pair_rates(pairs, "dest_code", pairs.month.unique())
        self.assertAlmostEqual(rate.loc["d"], .2)

    def test_unpublished_city_month_stays_unknown(self):
        od = pd.DataFrame({"month": ["2022-01", "2022-02", "2022-02"],
                           "origin_code": "o", "dest_code": ["r", "r", "c"],
                           "dest_kab_code": ["34.02", "34.02", "34.71"],
                           "n_homed_maids": 100, "n_maids": [20, 20, 10],
                           "visit_rate": [.2, .2, .1], "is_intra": False})
        result = city_visits(od)
        unknown = result.loc[("o", "2022-01")]
        self.assertTrue(pd.isna(unknown.city_visits))
        self.assertTrue(pd.isna(unknown.city_share))
        self.assertTrue(pd.isna(unknown.city_rate))
        complete = result.loc[("o", "2022-02")]
        self.assertAlmostEqual(complete.city_share, 100 / 3)
        self.assertAlmostEqual(complete.city_rate, .1)

    def test_duplicate_pair_month_rejected(self):
        pairs = pd.DataFrame({"month": ["2022-01", "2022-01"],
                              "dest_code": "d", "visit_rate": [.1, .2]})
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            complete_pair_rates(pairs, "dest_code", ["2022-01"])


if __name__ == "__main__":
    unittest.main()
