import json
import unittest
from pathlib import Path

from rsi4tun.one_one_proxy import (
    BACKEND,
    CONTRACT,
    FEATURE_IDS,
    fit_one_one_proxy,
    load_tune_rows,
    proxy_record,
)

ROOT = Path(__file__).resolve().parents[1]
TUNE = ROOT / "data" / "development" / "1-1" / "tune"
PROXY = ROOT / "dikw" / "wisdom" / "1_1_proxy.json"


class OneOneProxyTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_tune_rows(TUNE)
        self.proxy = fit_one_one_proxy(self.rows)
        self.saved = json.loads(PROXY.read_text())

    def test_every_tune_arm_is_a_row(self):
        arms = sorted(
            path.name
            for path in TUNE.iterdir()
            if path.is_dir() and path.name != "params"
        )
        self.assertEqual([row.run_id for row in self.rows], arms)
        self.assertEqual(len(self.rows), 46)
        self.assertIn("a45_a44_intensity_m1400", arms)

    def test_features_are_the_deployment_knobs(self):
        self.assertEqual(self.proxy.feature_ids, FEATURE_IDS)
        self.assertNotIn("k_wedge", FEATURE_IDS)
        by_id = {row.run_id: dict(row.features) for row in self.rows}
        self.assertEqual(by_id["a01_mirror_k"]["proud_mm"], 0.0)
        self.assertEqual(by_id["a02_proud_on_a01"]["proud_mm"], 5.0)
        self.assertEqual(by_id["a06_mid_mask_mirror_proud"]["mid_mask"], 1.0)
        self.assertEqual(by_id["a11_a08_proud_radius_015"]["mid_mask"], 0.0)
        a45 = by_id["a45_a44_intensity_m1400"]
        self.assertEqual(a45["ring2_shift"], 1.0)
        self.assertEqual(a45["theta_split"], 1.0)
        self.assertEqual(a45["dark_m1400"], 1.0)

    def test_a45_score_matches_observed_miou(self):
        a45 = next(row for row in self.rows if row.run_id == "a45_a44_intensity_m1400")
        score = self.proxy.predict(dict(a45.features), CONTRACT, BACKEND)
        self.assertLess(abs(score - a45.final_miou), 0.005)
        self.assertAlmostEqual(a45.final_miou, 0.917, places=3)
        best = max(
            self.rows,
            key=lambda row: self.proxy.predict(dict(row.features), CONTRACT, BACKEND),
        )
        self.assertEqual(best.run_id, a45.run_id)

    def test_saved_record_matches_the_fit_and_stays_unreleased(self):
        record = proxy_record(self.rows, self.proxy)
        self.assertEqual(record["proxy_id"], self.saved["proxy_id"])
        self.assertEqual(record["feature_ids"], self.saved["feature_ids"])
        self.assertEqual(record["centres"], self.saved["centres"])
        self.assertEqual(record["scales"], self.saved["scales"])
        self.assertEqual(record["weights"], self.saved["weights"])
        self.assertEqual(record["intercept"], self.saved["intercept"])
        self.assertEqual(record["fit_rows_digest"], self.saved["fit_rows_digest"])
        self.assertEqual(record["n_rows"], 46)
        self.assertEqual(record["validation_receipt"], "development_fit_pending")
        self.assertLess(abs(record["best_proxy_score"] - record["best_observed_miou"]), 0.005)
        with self.assertRaisesRegex(ValueError, "unvalidated_proxy"):
            self.proxy.score(dict(self.rows[-1].features), CONTRACT, BACKEND)
