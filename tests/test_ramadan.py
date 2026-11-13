"""Protect daily weighting, coverage, missingness and matched comparison dates."""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from applied import ramadan_analysis, ramadan_windows
from config import GOOGLE_CATEGORIES


class RamadanTests(unittest.TestCase):
    def setUp(self):
        self.before, self.during = ramadan_windows(pd.Timestamp('2022-04-03'))
        dates = self.before.union(self.during)
        self.h = pd.DataFrame([(c, c, 'TEST', d, h, 10 if d != dates[0] else 100)
                               for c in ['a', 'b'] for d in dates for h in range(24)],
                              columns=['kapanewon_code', 'kapanewon', 'kab_kota', 'date', 'hour', 'n_maids'])
        self.d = pd.DataFrame({f'g_{c}': 1. for c in GOOGLE_CATEGORIES}, index=dates)

    def run_data(self, h=None, d=None, **kw):
        return ramadan_analysis(self.h if h is None else h, self.d if d is None else d,
                                '2022-04-03', focus_codes=('a',), **kw)

    def test_windows_and_weekdays(self):
        r = self.run_data(exclude_paired_fridays=True)
        self.assertNotIn(pd.Timestamp('2022-04-02'), r['before'].union(r['during']))
        self.assertEqual(len(r['before']), 20)
        self.assertEqual(pd.Series(r['before'].day_of_week).value_counts().to_dict(),
                         pd.Series(r['during'].day_of_week).value_counts().to_dict())

    def test_daily_normalization_and_equal_day_weights(self):
        self.h.loc[(self.h.date == self.before[0]) & self.h.hour.isin([3, 4]), 'n_maids'] = 200
        r = self.run_data()
        expected = ((400 / 2600 * 100) + 20 * (2 / 24 * 100)) / 21
        self.assertAlmostEqual(r['summary'].set_index('kapanewon_code').loc['a', 'before'], expected)
        self.assertTrue(np.allclose(r['profiles'].groupby(['kapanewon_code', 'period']).share_pct.sum(), 100))

    def test_missing_hour_excludes_entire_nonfocal_area(self):
        r = self.run_data(h=self.h.drop(self.h[self.h.kapanewon_code.eq('b')].index[0]))
        self.assertEqual(set(r['summary'].kapanewon_code), {'a'})
        self.assertFalse(r['coverage'].set_index('kapanewon_code').loc['b', 'eligible'])

    def test_missing_focal_hour_fails_instead_of_zero_fill(self):
        with self.assertRaisesRegex(ValueError, 'focal area'):
            self.run_data(h=self.h.iloc[1:])

    def test_duplicate_hour_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.run_data(h=pd.concat([self.h, self.h.iloc[:1]]))

    def test_google_gaps_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Google'):
            self.run_data(d=self.d.iloc[1:])

    def test_google_change_is_difference_of_index_means(self):
        self.d.loc[self.before, 'g_parks'] = 20
        self.d.loc[self.during, 'g_parks'] = -5
        r = self.run_data()
        self.assertEqual(r['google'].set_index('category').loc['parks', 'change_pp'], -25)


if __name__ == '__main__':
    unittest.main()
