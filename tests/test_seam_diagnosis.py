import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np

from rsi4tun.seam_diagnosis import (
    classify_crops,
    compare_sealed_pattern,
    crop_rows_from_results,
    load_arm_artifacts,
    summarize_vector,
)


def _item(block, mask, score, pos, neg, left_top):
    h, w = mask.shape
    labels = np.array([1] * pos + [0] * neg, dtype=int)
    points = np.zeros((pos + neg, 2), dtype=float)
    return {
        "block": block,
        "mask": mask[None].astype(bool),
        "score": np.array([score], dtype=float),
        "labels": labels,
        "points": points,
        "left_top": left_top,
        "logit": np.zeros((256, 256), dtype=float),
        "cropped_image": np.zeros((h, w, 3), dtype=np.uint8),
    }


class SeamDiagnosisTests(unittest.TestCase):
    def test_area_ratio_uses_fullest_crop_of_block(self):
        full = np.ones((100, 50), dtype=bool)
        short = np.ones((30, 50), dtype=bool)
        results = [
            [
                _item("A2", short, 0.99, 11, 10, (0.0, 0.0)),
                _item("K", full, 0.95, 16, 24, (0.0, 40.0)),
            ],
            [
                _item("A2", full, 0.90, 56, 40, (60.0, 20.0)),
                _item("K", full, 0.94, 16, 24, (60.0, 40.0)),
            ],
        ]
        depth = np.ones((120, 120), dtype=np.float32)
        rows = crop_rows_from_results(results, depth)
        a2 = [row for row in rows if row.block == "A2"]
        self.assertAlmostEqual(a2[0].area_ratio, 0.3, places=5)
        self.assertAlmostEqual(a2[1].area_ratio, 1.0, places=5)
        self.assertTrue(a2[0].touches_top)
        self.assertFalse(a2[1].touches_top)

    def test_classifier_names_seam_and_complete_low_score(self):
        full = np.ones((100, 50), dtype=bool)
        short = np.ones((30, 50), dtype=bool)
        results = [
            [
                _item("A2", short, 0.99, 11, 10, (0.0, 0.0)),
                _item("K", full, 0.65, 16, 24, (0.0, 40.0)),
                _item("B1", full, 0.94, 56, 40, (0.0, 20.0)),
            ],
            [
                _item("A2", full, 0.90, 56, 40, (60.0, 20.0)),
                _item("K", full, 0.95, 16, 24, (60.0, 40.0)),
                _item("B1", full, 0.93, 56, 40, (60.0, 20.0)),
            ],
        ]
        depth = np.ones((120, 120), dtype=np.float32)
        rows = crop_rows_from_results(results, depth)
        report = classify_crops(rows)
        self.assertTrue(report.seam_open)
        self.assertEqual(report.seam_blocks, ("A2",))
        self.assertEqual(report.complete_low_score[0].block, "K")
        self.assertLess(report.complete_low_score[0].score, 0.7)
        self.assertLess(report.border_area_ratio, 0.5)

    def test_depth_validity_reported_on_border_crop(self):
        short = np.ones((30, 40), dtype=bool)
        results = [[_item("A2", short, 0.99, 11, 10, (0.0, 0.0))]]
        depth = np.ones((100, 80), dtype=np.float32)
        depth[:15, :] = 0.0
        rows = crop_rows_from_results(results, depth)
        self.assertLess(rows[0].depth_validity, 0.6)
        self.assertGreater(rows[0].depth_validity, 0.4)

    def test_summarize_vector_exposes_gate_fields(self):
        full = np.ones((100, 50), dtype=bool)
        short = np.ones((30, 50), dtype=bool)
        results = [
            [
                _item("A2", short, 0.99, 11, 10, (0.0, 0.0)),
                _item("K", full, 0.65, 16, 24, (0.0, 40.0)),
            ]
        ]
        depth = np.ones((120, 120), dtype=np.float32)
        report = classify_crops(crop_rows_from_results(results, depth))
        payload = summarize_vector(report)
        self.assertIn("seam_open", payload)
        self.assertIn("border_area_ratio", payload)
        self.assertIn("complete_low_score", payload)

    def test_load_arm_artifacts_reads_results_and_depth(self):
        full = np.ones((20, 10), dtype=bool)
        results = [[_item("K", full, 0.9, 4, 4, (0.0, 0.0))]]
        depth = np.ones((40, 40), dtype=np.float32)
        with tempfile.TemporaryDirectory() as tmp:
            arm = Path(tmp)
            with (arm / "results.pkl").open("wb") as handle:
                pickle.dump(results, handle)
            np.save(arm / "depth_map.npy", depth)
            loaded_results, loaded_depth = load_arm_artifacts(arm)
            self.assertEqual(len(loaded_results), 1)
            self.assertEqual(loaded_depth.shape, depth.shape)

    def test_compare_sealed_pattern_rules(self):
        full = np.ones((100, 50), dtype=bool)
        results = [[_item("A2", full, 0.90, 56, 40, (10.0, 20.0))]]
        depth = np.ones((120, 120), dtype=np.float32)
        report = classify_crops(crop_rows_from_results(results, depth))
        sealed = {"predicted_border_area_ratio": 0.9}
        self.assertEqual(
            compare_sealed_pattern(sealed, report, baseline_miou=0.849, observed_miou=0.870),
            "both_moved",
        )
        self.assertEqual(
            compare_sealed_pattern(sealed, report, baseline_miou=0.849, observed_miou=0.850),
            "metric_not_target",
        )
        short = np.ones((30, 50), dtype=bool)
        short_report = classify_crops(
            crop_rows_from_results(
                [
                    [_item("A2", short, 0.99, 11, 10, (0.0, 0.0)), _item("K", full, 0.95, 16, 24, (0.0, 40.0))],
                    [_item("A2", full, 0.90, 56, 40, (60.0, 20.0)), _item("K", full, 0.94, 16, 24, (60.0, 40.0))],
                ],
                depth,
            )
        )
        self.assertEqual(
            compare_sealed_pattern(sealed, short_report, baseline_miou=0.849, observed_miou=0.870),
            "treatment_failed",
        )


if __name__ == "__main__":
    unittest.main()
