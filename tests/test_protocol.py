from dataclasses import replace
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from rsi4tun import evidence, hypotheses
from rsi4tun.contracts import FULL_STAGES, digest, file_digest, read_json, run_from_dict, save_once
from rsi4tun.demo import run_demo
from rsi4tun.diagnosis import Arm, HypothesisProgram, build_plan, classify_responses
from rsi4tun.proxy import derive_signals, propose_proxy
from rsi4tun.records import append_outcome, assess_knowledge_promotion, preregister, verify_preregistration
from rsi4tun.researcher import build_context


def fixture(overlap=False, signal_change=None):
    comparison = {
        "status": "comparable",
        "features": {"depth_valid_coverage__delta": -0.25, "k_phase_rms_turns__delta": 0.15,
                     "boundary_symmetric_distance_fraction__delta": 0.04},
        "provenance": {"reference_bundle_digest": digest("reference")},
    }
    signals = tuple(signal for signal in derive_signals(comparison, file_digest(Path(evidence.__file__)), digest("reference"))
                    if signal.feature_id == "boundary_symmetric_distance_fraction__delta")
    if signal_change is not None:
        signals = (replace(signals[0], **signal_change),)
    source = file_digest(Path(hypotheses.__file__))
    first = HypothesisProgram("h1", "rsi4tun.hypotheses:depth_limits_k", source,
                              (("interval_half_width", 0.005), ("depth_to_k", 0.4), ("direct_phase_effect", 1.0)),
                              "dikw/knowledge/hypotheses/fixture.md")
    second = HypothesisProgram("h2", "rsi4tun.hypotheses:phase_limits_k", source,
                               (("interval_half_width", 0.005), ("incidental_depth_effect", 0.4 if overlap else 0.0), ("phase_to_k", 1.0)),
                               "dikw/knowledge/hypotheses/fixture.md")
    arms = (Arm("A", "commit-a", "tree-a", (("depth_repair_fraction", 0.25),)),
            Arm("B", "commit-b", "tree-b", (("phase_correction_turns", 0.05),)))
    arguments = {
        "experiment_id": "protocol-fixture",
        "baseline_run_id": "baseline-run",
        "baseline_commit": "baseline-commit",
        "comparison": comparison,
        "candidate_signals": signals,
        "proxy_digest": digest("proxy"),
        "evidence_contract_digest": digest("contract"),
        "arms": arms,
        "hypotheses": (first, second),
        "thresholds": (("depth_valid_coverage__delta", 0.01), ("k_phase_rms_turns__delta", 0.01),
                       ("boundary_symmetric_distance_fraction__delta", 0.005)),
        "units": (("depth_valid_coverage__delta", "fraction"), ("k_phase_rms_turns__delta", "turns"),
                  ("boundary_symmetric_distance_fraction__delta", "circumference_fraction")),
        "manipulation_intervals": (("A", "depth_repair_fraction", 0.24, 0.26), ("B", "phase_correction_turns", 0.04, 0.06)),
        "knowledge_ref": "dikw/information/research_notes/protocol_fixture.md",
    }
    interventions = {"A": {"depth_repair_fraction": 0.25}, "B": {"phase_correction_turns": 0.05}}
    return arguments, comparison, signals, interventions


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.arguments, self.comparison, self.signals, self.interventions = fixture()
        self.plan = build_plan(**self.arguments)

    def matching_responses(self):
        return {arm: {metric: (bounds[0] + bounds[1]) / 2 for metric, bounds in outcomes.items()}
                for arm, outcomes in self.plan.predictions[0].items()}

    def register(self, directory):
        root = Path(directory)
        comparison_path = root / "comparison.json"
        signal_path = root / "signals.json"
        save_once(comparison_path, self.comparison)
        save_once(signal_path, self.signals)
        path, before_digest = preregister(root / "rst", self.plan, campaign_id="synthetic-fixture", synthetic=True,
                                         comparison_path=str(comparison_path), signal_path=str(signal_path))
        return path, before_digest, comparison_path, signal_path

    def test_both_arms_can_respond_and_one_hypothesis_can_match(self):
        responses = self.matching_responses()
        self.assertNotEqual(responses["A"]["k_phase_rms_turns__delta"], 0.0)
        self.assertNotEqual(responses["B"]["k_phase_rms_turns__delta"], 0.0)
        result = classify_responses(self.plan, responses, self.interventions)
        self.assertEqual(result["status"], "h1_supported")
        self.assertEqual(result["matches"], (True, False))
        self.assertEqual(result["causal_status"], "unconfirmed")
        self.assertEqual(result["candidate_validation_status"], "development_required")

    def test_null_response_is_inconclusive_when_intervention_was_applied(self):
        responses = {arm.arm_id: {metric: 0.0 for metric, _ in self.plan.thresholds} for arm in self.plan.arms}
        result = classify_responses(self.plan, responses, self.interventions)
        self.assertEqual(result["status"], "neither_supported")
        self.assertTrue(result["manipulation_valid"])
        self.assertFalse(result["response_above_noise"])
        self.assertEqual(result["causal_status"], "unconfirmed")

    def test_failed_manipulation_is_separate_from_hypothesis_matching(self):
        interventions = {"A": {"depth_repair_fraction": 0.0}, "B": {"phase_correction_turns": 0.05}}
        result = classify_responses(self.plan, self.matching_responses(), interventions)
        self.assertEqual(result["status"], "invalid_manipulation")
        self.assertFalse(result["manipulation_valid"])

    def test_overlapping_predictions_are_rejected_before_execution(self):
        arguments, _, _, _ = fixture(overlap=True)
        with self.assertRaisesRegex(ValueError, "predictions_not_distinguishable"):
            build_plan(**arguments)

    def test_candidate_signals_must_come_from_current_comparison(self):
        arguments, _, _, _ = fixture(signal_change={"comparison_digest": digest("other-comparison")})
        with self.assertRaisesRegex(ValueError, "signals_from_different_evidence"):
            build_plan(**arguments)

    def test_candidate_signal_must_name_a_measured_feature(self):
        arguments, _, _, _ = fixture(signal_change={"feature_id": "unmeasured_signal"})
        with self.assertRaises(ValueError):
            build_plan(**arguments)

    def test_proxy_proposal_is_derived_and_bound_before_diagnosis(self):
        proposal = propose_proxy(self.signals, self.arguments["proxy_digest"])
        self.assertEqual(self.plan.candidate_proxy_digest, digest(proposal))
        self.assertEqual(proposal.status, "development_validation_required")
        with self.assertRaisesRegex(ValueError, "candidate_proxy_not_derived_from_comparison"):
            build_plan(**dict(self.arguments, candidate_proxy=replace(proposal, estimator="unregistered_estimator")))

    def test_unavailable_reference_comparison_cannot_open_diagnosis(self):
        comparison = dict(self.comparison, status="coverage_gap", features={})
        arguments = dict(self.arguments, comparison=comparison)
        with self.assertRaisesRegex(ValueError, "comparison_required_before_diagnosis"):
            build_plan(**arguments)

    def test_hypothesis_code_version_is_checked(self):
        hypotheses_pair = (replace(self.arguments["hypotheses"][0], source_sha256="0" * 64), self.arguments["hypotheses"][1])
        with self.assertRaisesRegex(ValueError, "hypothesis_code_changed"):
            build_plan(**dict(self.arguments, hypotheses=hypotheses_pair))

    def test_preregistration_is_write_once_and_comparison_is_bound(self):
        with TemporaryDirectory() as directory:
            path, before_digest, comparison_path, signal_path = self.register(directory)
            before = verify_preregistration(path, before_digest, self.plan)
            self.assertTrue(before["synthetic"])
            self.assertFalse(before["learning_eligible"])
            with self.assertRaises(FileExistsError):
                preregister(path.parent, self.plan, campaign_id="synthetic-fixture", synthetic=True,
                            comparison_path=str(comparison_path), signal_path=str(signal_path))
            changed = dict(self.comparison, features=dict(self.comparison["features"], extra=0.1))
            comparison_path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "comparison_record_changed"):
                verify_preregistration(path, before_digest, self.plan)

    def test_contradictory_outcome_cannot_be_saved(self):
        with TemporaryDirectory() as directory:
            path, before_digest, _, _ = self.register(directory)
            original = classify_responses(self.plan, self.matching_responses(), self.interventions)
            for changes in ({"status": "neither_supported"}, {"causal_status": "confirmed"}):
                with self.subTest(changes=changes):
                    with self.assertRaisesRegex(ValueError, "diagnosis_response_contradiction"):
                        append_outcome(path, before_digest, self.plan, diagnosis=dict(original, **changes),
                                       run_ids=("run-a", "run-b"), code_commits=("commit-a", "commit-b"),
                                       treatment_decisions=(), next_action="development_review",
                                       knowledge_ref="dikw/information/research_notes/fixture.md")

    def test_synthetic_results_cannot_promote_scientific_knowledge(self):
        request = {"claim_id": "claim", "claim_kind": "scoped_intervention_response", "scope_id": "scope",
                   "assumptions_ref": "dikw/knowledge/assumptions.md", "counterexamples_ref": "dikw/knowledge/counterexamples.md",
                   "code_commit": "commit", "knowledge_ref": "dikw/knowledge/claims/claim.md"}
        evidence_records = ({"synthetic": True, "learning_eligible": False, "status": "h1_supported"},)
        tests = ({"passed": True, "test_code_digest": digest("test"), "evidence_digest": digest(evidence_records[0]),
                  "claim_id": "claim", "code_commit": "commit"},)
        result = assess_knowledge_promotion(request, evidence_records, tests)
        self.assertEqual(result["decision"], "reject_fixture_or_ineligible_evidence")

    def test_retrieved_claims_cannot_leak_ground_truth_into_context(self):
        claim = {"claim_id": "claim", "status": "accepted", "scope_id": "scope", "synthetic": False,
                 "evidence_digests": (digest("evidence"),), "test_digests": (digest("test"),), "level": "knowledge",
                 "evidence_payload": {"final_miou": 0.9}}
        with self.assertRaisesRegex(ValueError, "private_development_field"):
            build_context(self.comparison, self.signals, proxy_digest=digest("proxy"), code_revision="commit",
                          claim_registry=(claim,), scope_id="scope", budget_full_runs=2)

    def test_nonfinite_response_cannot_match_a_hypothesis(self):
        responses = self.matching_responses()
        responses["A"]["k_phase_rms_turns__delta"] = float("nan")
        with self.assertRaisesRegex(ValueError, "non_finite_measurement"):
            classify_responses(self.plan, responses, self.interventions)

    def test_demo_executes_registered_full_runs_and_retains_executable_code(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "demo"
            report = run_demo(output)
            self.assertTrue(report["synthetic"])
            self.assertFalse(report["learning_eligible"])
            self.assertFalse(report["real_sam_executed"])
            self.assertFalse(report["scientific_knowledge_promoted"])
            self.assertEqual(report["new_proxy_development_validation"], "not_performed_by_fixture")
            self.assertEqual(report["diagnosis"], "h1_supported")
            self.assertEqual(report["causal_status"], "unconfirmed")
            self.assertEqual(report["rollback_status"], "rollback")
            self.assertTrue(report["rollback_preserved_accepted_commit"])
            self.assertEqual(report["plateau_status"], "plateau")
            run_paths = sorted((output / "runs").glob("*/run.json"))
            self.assertEqual(len(run_paths), report["full_pipeline_runs"])
            self.assertEqual(len(run_paths), 6)
            for run_path in run_paths:
                run = run_from_dict(read_json(run_path))
                run.require_complete()
                self.assertEqual(run.stage_trace, FULL_STAGES)
            before = read_json(Path(report["rst_before"]))
            after = read_json(Path(report["rst_after"]))
            self.assertEqual(after["before_digest"], digest(before))
            receipts = [read_json(path) for path in (output / "archive" / "executions").glob("*.json")]
            registered = [receipt for receipt in receipts if receipt["registration_digest"] is not None]
            self.assertEqual(len(registered), 2)
            self.assertEqual({receipt["registration_digest"] for receipt in registered}, {digest(before)})
            self.assertEqual({receipt["revision_commit"] for receipt in registered}, set(after["code_commits"]))
            accepted = subprocess.run(("git", "rev-parse", "refs/rsi/accepted"), cwd=output / "code", capture_output=True, text=True, check=True)
            self.assertEqual(accepted.stdout.strip(), report["accepted_commit"])
            contents = subprocess.run(("git", "bundle", "list-heads", report["accepted_bundle"]), cwd=output / "code", capture_output=True, text=True, check=True)
            self.assertIn(report["accepted_commit"], contents.stdout)
            self.assertFalse(read_json(output / "rst" / "warning.json")["sent"])


if __name__ == "__main__":
    unittest.main()
