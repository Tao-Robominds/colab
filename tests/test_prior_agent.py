import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import numpy as np

from prior_agent.client import parse_action
from prior_agent.dikw import maybe_refit_1_1_proxy, maybe_refit_seam_proxy
from prior_agent.loop import run_episode, seal_prediction
from prior_agent.runner import filter_overrides, lining_guard, load_gt_labels, relay_output


class PriorAgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        self._seed_repo(self.root)
        self.calls = []
        self.runner_called_after_prediction = []

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _seed_repo(self, root: Path):
        (root / ".cursor/rules/private").mkdir(parents=True)
        (root / ".cursor/rules/private/identity.mdc").write_text(
            "---\nalwaysApply: true\n---\n\nI pursue novelty through evidence.\n"
        )
        (root / "dikw/wisdom").mkdir(parents=True)
        (root / "dikw/wisdom/staggered_tune_experience.md").write_text("# experience\n")
        (root / "dikw/wisdom/sample_proxy.json").write_text(
            json.dumps(
                {
                    "feature_ids": ["k_wedge", "angle_positive", "ab_rel_error", "proud_cut"],
                    "centres": [0.0, 1.0, 0.0, 0.0],
                    "scales": [1.0, 1.0, 1.0, 1.0],
                    "weights": [0.01, 0.1, -0.01, 0.02],
                    "intercept": 0.78,
                }
            )
        )
        (root / "configs/families/staggered").mkdir(parents=True)
        for name, body in {
            "parameters_family.json": {"family_mode": "staggered"},
            "parameters_sam.json": {"mirror_k_geometry": False, "AB_height": 3239.77, "angle": 7.52},
            "parameters_denoising.json": {"mask_r_low": 2.32, "mask_r_high": 2.79, "smoothing_offset": -0.003},
            "parameters_enhancing.json": {"window_size": 9},
            "parameters_detecting.json": {},
            "parameters_unfolding.json": {},
        }.items():
            (root / "configs/families/staggered" / name).write_text(json.dumps(body) + "\n")
        base = root / "data/development/1-1/baseline"
        (base / "evaluation").mkdir(parents=True)
        (root / "data/scans").mkdir(parents=True)
        (root / "data/scans/1-1.txt").write_text("0 0 0 2.75 0 0\n0 0 0 2.75 1 0\n")
        (base / "only_label.csv").write_text("pred_labels,pred_rings\n0,-1\n1,-1\n")
        (base / "final.csv").write_text("h,theta,r,pred\n0,0,2.75,0\n0,0,2.75,1\n")
        (base / "evaluation/performance.md").write_text(
            "\n".join(
                [
                    "# Performance Metrics for Tunnel baseline",
                    "## Overall Metrics",
                    "- Mean IoU (mIoU): 0.785",
                    "## Per-class IoU",
                    "- Background: 0.813",
                    "- K-block: 0.716",
                    "- B1-block: 0.859",
                    "- A1-block: 0.799",
                    "- A2-block: 0.624",
                    "- A3-block: 0.815",
                    "- B2-block: 0.872",
                ]
            )
            + "\n"
        )

    def _write_metrics(self, run_dir: Path, miou: float, k: float = 0.720):
        eval_dir = run_dir / "evaluation"
        eval_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "only_label.csv").write_text("pred_labels,pred_rings\n0,-1\n1,-1\n")
        (eval_dir / "performance.md").write_text(
            "\n".join(
                [
                    f"# Performance Metrics for Tunnel {run_dir.name}",
                    "## Overall Metrics",
                    f"- Mean IoU (mIoU): {miou:.3f}",
                    "## Per-class IoU",
                    "- Background: 0.820",
                    f"- K-block: {k:.3f}",
                    "- B1-block: 0.860",
                    "- A1-block: 0.800",
                    "- A2-block: 0.630",
                    "- A3-block: 0.820",
                    "- B2-block: 0.870",
                ]
            )
            + "\n"
        )

    def test_chat_context_stays_one_turn(self):
        actions = [
            {
                "action": "full_run",
                "name": "t01_mirror",
                "predicted_miou": 0.800,
                "rationale": "UNIQUE_RATIONALE_SHOULD_NOT_ECHO",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.800,
                "rationale": "stop",
                "stop_reason": "budget",
            },
        ]
        seen = []

        def chat(messages):
            seen.append(messages)
            return json.dumps(actions.pop(0))

        def run_full(root, tune_root, arm_name, params_dir, scan_path, subset_id):
            run_dir = tune_root / arm_name
            self._write_metrics(run_dir, 0.800)
            return run_dir

        run_episode(
            self.root,
            tunnel_id="1-1",
            target=0.9,
            max_full_runs=2,
            chat=chat,
            run_full=run_full,
            run_proud=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no proud")),
        )
        self.assertGreaterEqual(len(seen), 2)
        for messages in seen:
            self.assertLessEqual(len(messages), 2)
        second = "\n".join(item["content"] for item in seen[1])
        self.assertNotIn("UNIQUE_RATIONALE_SHOULD_NOT_ECHO", second)

    def test_gt_labels_read_one_column(self):
        labels = load_gt_labels(self.root / "data/scans/1-1.txt")
        self.assertEqual(labels.tolist(), [0, 1])

    def test_relay_output_keeps_only_the_tail(self):
        import io

        short = io.BytesIO(b"hi\n")
        short_dest = io.BytesIO()
        relay_output(short, short_dest, max_bytes=64)
        self.assertEqual(short_dest.getvalue(), b"hi\n")

        long = io.BytesIO(b"abcdefghij")
        long_dest = io.BytesIO()
        relay_output(long, long_dest, max_bytes=4)
        body = long_dest.getvalue()
        self.assertTrue(body.endswith(b"ghij"))
        self.assertIn(b"dropped", body)
        self.assertLess(len(body), 80)

    def test_parse_action_strips_fence(self):
        text = '```json\n{"action": "stop", "predicted_miou": 0.8, "rationale": "done"}\n```'
        action = parse_action(text)
        self.assertEqual(action["action"], "stop")

    def test_filter_rejects_unknown_key(self):
        with self.assertRaises(ValueError):
            filter_overrides({"parameters_sam.json": {"unknown": 1}})

    def test_prediction_sealed_before_runner(self):
        actions = [
            {
                "action": "full_run",
                "name": "t01_mirror",
                "predicted_miou": 0.800,
                "rationale": "mirror",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.800,
                "rationale": "stop",
                "stop_reason": "budget",
            },
        ]

        def chat(_messages):
            return json.dumps(actions.pop(0))

        def run_full(root, tune_root, arm_name, params_dir, scan_path, subset_id):
            pred = tune_root / f"{arm_name}_PREDICTION.md"
            self.runner_called_after_prediction.append(pred.is_file())
            run_dir = tune_root / arm_name
            self._write_metrics(run_dir, 0.800)
            return run_dir

        summary = run_episode(
            self.root,
            tunnel_id="1-1",
            target=0.9,
            max_full_runs=2,
            chat=chat,
            run_full=run_full,
            run_proud=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no proud")),
        )
        self.assertEqual(self.runner_called_after_prediction, [True])
        self.assertEqual(summary["full_runs"], 1)
        self.assertFalse(summary["reached_target"])
        tune = self.root / "data/development/1-1/tune"
        self.assertTrue((tune / "t01_mirror_PREDICTION.md").is_file())
        self.assertTrue((tune / "t01_mirror_result.json").is_file())
        self.assertTrue((tune / "t01_mirror" / "evaluation" / "performance.md").is_file())
        self.assertFalse((tune / "t01_mirror" / "baseline").exists())

    def test_lining_guard_failure_recorded(self):
        classes = {
            "K-block": 0.600,
            "B1-block": 0.860,
            "A1-block": 0.800,
            "A2-block": 0.630,
            "A3-block": 0.820,
            "B2-block": 0.870,
        }
        base = {
            "K-block": 0.716,
            "B1-block": 0.859,
            "A1-block": 0.799,
            "A2-block": 0.624,
            "A3-block": 0.815,
            "B2-block": 0.872,
        }
        ok, fails = lining_guard(classes, base)
        self.assertFalse(ok)
        self.assertTrue(any(item.startswith("K-block") for item in fails))

        actions = [
            {
                "action": "full_run",
                "name": "t01_bad",
                "predicted_miou": 0.900,
                "rationale": "bad",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.785,
                "rationale": "stop",
            },
        ]

        def chat(_messages):
            return json.dumps(actions.pop(0))

        def run_full(root, tune_root, arm_name, params_dir, scan_path, subset_id):
            run_dir = tune_root / arm_name
            self._write_metrics(run_dir, 0.790, k=0.600)
            return run_dir

        summary = run_episode(
            self.root,
            chat=chat,
            run_full=run_full,
            run_proud=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no proud")),
        )
        self.assertFalse(summary["history"][0]["guard_ok"])
        knowledge = (self.root / "dikw/information/research_notes/1_1_tune.md").read_text()
        self.assertIn("Lining guard passed: False", knowledge)

    def test_resume_keeps_completed_arms(self):
        tune = self.root / "data/development/1-1/tune"
        tune.mkdir(parents=True)
        arm = tune / "a01_mirror_k"
        self._write_metrics(arm, 0.796, k=0.797)
        (tune / "a01_mirror_k_PREDICTION.md").write_text(
            json.dumps(
                {
                    "action": "full_run",
                    "name": "a01_mirror_k",
                    "predicted_miou": 0.797,
                    "rationale": "mirror",
                    "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
                }
            )
            + "\n"
        )
        (tune / "a01_mirror_k_result.json").write_text(
            json.dumps(
                {
                    "name": "a01_mirror_k",
                    "action": "full_run",
                    "predicted_miou": 0.797,
                    "mIoU": 0.796,
                    "spill": 10,
                    "guard_ok": True,
                    "guard_fails": [],
                    "prediction_held": True,
                    "classes": {
                        "Background": 0.803,
                        "K-block": 0.797,
                        "B1-block": 0.863,
                        "A1-block": 0.790,
                        "A2-block": 0.622,
                        "A3-block": 0.815,
                        "B2-block": 0.879,
                    },
                }
            )
            + "\n"
        )
        (tune / "a02_mirror_proud_PREDICTION.md").write_text(
            json.dumps(
                {
                    "action": "proud_replay",
                    "name": "a02_mirror_proud",
                    "predicted_miou": 0.799,
                    "rationale": "proud",
                    "source_arm": "a01_mirror_k",
                }
            )
            + "\n"
        )
        (tune / "a02_mirror_proud").mkdir()
        actions = [
            {
                "action": "full_run",
                "name": "a01_mirror_k",
                "predicted_miou": 0.797,
                "rationale": "repeat",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.796,
                "rationale": "stop",
            },
        ]
        run_calls = []

        def chat(_messages):
            return json.dumps(actions.pop(0))

        def run_full(root, tune_root, arm_name, params_dir, scan_path, subset_id):
            run_calls.append(arm_name)
            run_dir = tune_root / arm_name
            self._write_metrics(run_dir, 0.850)
            return run_dir

        summary = run_episode(
            self.root,
            chat=chat,
            run_full=run_full,
            run_proud=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no proud")),
        )
        self.assertEqual(run_calls, [])
        self.assertEqual(summary["full_runs"], 1)
        self.assertEqual(summary["best"]["name"], "a01_mirror_k")
        self.assertEqual(summary["history"][0]["name"], "a01_mirror_k")
        self.assertFalse((tune / "a02_mirror_proud_PREDICTION.md").exists())
        self.assertFalse((tune / "a02_mirror_proud").exists())

    def test_sample_proxy_not_rewritten(self):
        sample_path = self.root / "dikw/wisdom/sample_proxy.json"
        before = sample_path.read_text()
        actions = [
            {
                "action": "full_run",
                "name": "t01_mirror",
                "predicted_miou": 0.800,
                "rationale": "mirror",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.800,
                "rationale": "stop",
            },
        ]

        def chat(_messages):
            return json.dumps(actions.pop(0))

        def run_full(root, tune_root, arm_name, params_dir, scan_path, subset_id):
            run_dir = tune_root / arm_name
            self._write_metrics(run_dir, 0.900)
            return run_dir

        run_episode(
            self.root,
            chat=chat,
            run_full=run_full,
            run_proud=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no proud")),
        )
        self.assertEqual(sample_path.read_text(), before)
        self.assertTrue((self.root / "dikw/wisdom/1_1_proxy.json").is_file())

    def _write_seam_arm(self, tune: Path, name: str = "a13_a08_proud_radius_007"):
        arm = tune / name
        arm.mkdir(parents=True)
        short = np.ones((30, 50), dtype=bool)
        full = np.ones((100, 50), dtype=bool)

        def item(block, mask, score, pos, neg, left_top):
            return {
                "block": block,
                "mask": mask[None],
                "score": np.array([score]),
                "labels": np.array([1] * pos + [0] * neg),
                "points": np.zeros((pos + neg, 2)),
                "left_top": left_top,
                "logit": np.zeros((256, 256)),
                "cropped_image": np.zeros((*mask.shape, 3), dtype=np.uint8),
            }

        results = [
            [
                item("A2", short, 0.99, 11, 10, (0.0, 0.0)),
                item("K", full, 0.65, 16, 24, (0.0, 40.0)),
            ],
            [
                item("A2", full, 0.90, 56, 40, (60.0, 20.0)),
                item("K", full, 0.95, 16, 24, (60.0, 40.0)),
            ],
        ]
        with (arm / "results.pkl").open("wb") as handle:
            import pickle

            pickle.dump(results, handle)
        np.save(arm / "depth_map.npy", np.ones((120, 120), dtype=np.float32))
        (arm / "state.pkl").write_bytes(b"state")
        self._write_metrics(arm, 0.849)
        return arm

    def test_seam_gate_rejects_non_wrap_action(self):
        tune = self.root / "data/development/1-1/tune"
        tune.mkdir(parents=True)
        self._write_seam_arm(tune)
        seen = []
        actions = [
            {
                "action": "full_run",
                "name": "bad_full",
                "predicted_miou": 0.860,
                "rationale": "ignore seam",
                "overrides": {"parameters_sam.json": {"mirror_k_geometry": True}},
            },
            {
                "action": "sam_replay",
                "name": "a40_wrap",
                "source_arm": "a13_a08_proud_radius_007",
                "predicted_miou": 0.870,
                "predicted_border_area_ratio": 0.9,
                "predicted_hold": {"interior_area": True, "complete_low_score": True},
                "rationale": "wrap",
                "overrides": {"parameters_sam.json": {"wrap_theta": True}},
            },
            {
                "action": "stop",
                "name": "done",
                "predicted_miou": 0.870,
                "rationale": "stop",
            },
        ]

        def chat(messages):
            seen.append(json.loads(messages[1]["content"]))
            return json.dumps(actions.pop(0))

        def run_sam(root, tune_root, arm_name, source_arm, params_dir, scan_path, subset_id):
            run_dir = tune_root / arm_name
            run_dir.mkdir(parents=True, exist_ok=True)
            full = np.ones((100, 50), dtype=bool)
            results = [
                [
                    {
                        "block": "A2",
                        "mask": full[None],
                        "score": np.array([0.90]),
                        "labels": np.array([1] * 56 + [0] * 40),
                        "points": np.zeros((96, 2)),
                        "left_top": (10.0, 20.0),
                        "logit": np.zeros((256, 256)),
                        "cropped_image": np.zeros((100, 50, 3), dtype=np.uint8),
                    }
                ]
            ]
            import pickle

            with (run_dir / "results.pkl").open("wb") as handle:
                pickle.dump(results, handle)
            np.save(run_dir / "depth_map.npy", np.ones((120, 120), dtype=np.float32))
            self._write_metrics(run_dir, 0.870)
            return run_dir

        summary = run_episode(
            self.root,
            chat=chat,
            run_full=lambda *a, **k: (_ for _ in ()).throw(AssertionError("no full")),
            run_proud=lambda *a, **k: (_ for _ in ()).throw(AssertionError("no proud")),
            run_sam=run_sam,
        )
        self.assertTrue(any(item.get("notice", {}).get("error") == "seam_requires_wrap_theta" for item in seen))
        self.assertEqual(summary["best"]["name"], "a40_wrap")
        self.assertTrue((self.root / "dikw/wisdom/1_1_proxy_seam.json").is_file())

    def test_sam_replay_requires_sealed_fields(self):
        path = self.root / "pred.json"
        with self.assertRaisesRegex(ValueError, "prediction_missing:predicted_border_area_ratio"):
            seal_prediction(
                path,
                {
                    "action": "sam_replay",
                    "predicted_miou": 0.87,
                    "rationale": "wrap",
                    "source_arm": "a13",
                },
            )

    def test_seam_proxy_skips_when_miou_flat(self):
        rows = [
            {
                "run_id": "baseline",
                "features": {
                    "k_wedge": 0.0,
                    "angle_positive": 1.0,
                    "ab_rel_error": 0.0,
                    "proud_cut": 0.0,
                    "border_area_ratio": 0.3,
                },
                "miou": 0.849,
                "is_baseline": True,
            },
            {
                "run_id": "wrap",
                "features": {
                    "k_wedge": 1.0,
                    "angle_positive": 1.0,
                    "ab_rel_error": 0.0,
                    "proud_cut": 1.0,
                    "border_area_ratio": 0.95,
                },
                "miou": 0.850,
                "is_baseline": False,
            },
        ]
        out = maybe_refit_seam_proxy(
            self.root / "dikw/wisdom",
            rows,
            border_area_ratio=0.95,
            baseline_miou=0.849,
            latest_miou=0.850,
        )
        self.assertIsNone(out)
        self.assertFalse((self.root / "dikw/wisdom/1_1_proxy_seam.json").is_file())

    def test_short_episode_does_not_replace_archive_proxy(self):
        wisdom = self.root / "dikw/wisdom"
        archive = wisdom / "1_1_proxy.json"
        archive.write_text(json.dumps({"n_rows": 46, "proxy_id": "1_1_tune_v2"}) + "\n")
        out = maybe_refit_1_1_proxy(
            wisdom,
            wisdom / "sample_proxy.json",
            [
                {
                    "run_id": "a01",
                    "features": {
                        "k_wedge": 1.0,
                        "angle_positive": 1.0,
                        "ab_rel_error": 0.0,
                        "proud_cut": 1.0,
                    },
                    "miou": 0.8,
                }
            ],
            {
                "k_wedge": 1.0,
                "angle_positive": 1.0,
                "ab_rel_error": 0.0,
                "proud_cut": 1.0,
            },
            0.8,
        )
        self.assertIsNone(out)
        self.assertEqual(json.loads(archive.read_text())["proxy_id"], "1_1_tune_v2")
