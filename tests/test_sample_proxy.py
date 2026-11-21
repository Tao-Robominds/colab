import json
import unittest
from pathlib import Path

from rsi4tun.sample_proxy import (
    AB_NOMINAL,
    BACKEND,
    CONTRACT,
    FEATURE_IDS,
    features,
    fit_sample_proxy,
    proxy_record,
)


class SampleProxyTests(unittest.TestCase):
    def setUp(self):
        self.proxy = fit_sample_proxy()
        self.path = Path(__file__).resolve().parents[1] / "dikw" / "wisdom" / "sample_proxy.json"
        self.saved = json.loads(self.path.read_text())

    def test_saved_coefficients_match_refit(self):
        record = proxy_record(self.proxy)
        self.assertEqual(record["feature_ids"], list(FEATURE_IDS))
        self.assertEqual(record["feature_ids"], self.saved["feature_ids"])
        self.assertEqual(record["centres"], self.saved["centres"])
        self.assertEqual(record["scales"], self.saved["scales"])
        self.assertEqual(record["weights"], self.saved["weights"])
        self.assertEqual(record["intercept"], self.saved["intercept"])
        self.assertEqual(record["fit_rows_digest"], self.saved["fit_rows_digest"])
        self.assertEqual(record["validation_receipt"], "development_fit_pending")
        self.assertEqual(self.saved["n_rows"], 31)

    def test_negative_angle_scores_far_below_pretune(self):
        score = self.proxy.predict(dict(features(0, 0, AB_NOMINAL, 0)), CONTRACT, BACKEND)
        self.assertLess(score, 0.5)
        self.assertLess(score, 0.880)

    def test_t22_control_stays_below_point_nine(self):
        score = self.proxy.predict(dict(features(1, 1, AB_NOMINAL, 0)), CONTRACT, BACKEND)
        self.assertLess(score, 0.900)

    def test_proud_cut_scores_above_point_nine(self):
        score = self.proxy.predict(dict(features(1, 1, AB_NOMINAL, 1)), CONTRACT, BACKEND)
        self.assertGreater(score, 0.900)
