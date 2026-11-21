import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

from prior_agent.client import parse_action
from prior_agent.loop import run_episode
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
        (root / "dikw/wisdom/sample_tune_strategy.md").write_text("# strategy\n")
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
        knowledge = (self.root / "dikw/knowledge/research_notes/1_1_tune.md").read_text()
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
