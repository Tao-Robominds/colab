from dataclasses import asdict, replace
import json
from pathlib import Path
import shutil
import subprocess
import sys

from rsi4tun import evidence, hypotheses
from rsi4tun.contracts import digest, file_digest, read_json, run_from_dict, save_once
from rsi4tun.diagnosis import Arm, HypothesisProgram, build_plan
from rsi4tun.evidence import ComparisonPolicy, bundle_from_dict
from rsi4tun.orchestrator import comparison_contract, decide_treatment, observe, preregister_and_execute
from rsi4tun.proxy import FrozenProxy, derive_signals, propose_proxy
from rsi4tun.records import append_outcome
from rsi4tun.versions import CodeStore, EvaluationReceipt


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(("git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                             "-c", "user.name=RSI4Tun Fixture", "-c", "user.email=fixture@localhost",
                             *arguments), cwd=repo, capture_output=True, text=True)
    if result.returncode:
        raise ValueError("fixture_git_failure:" + result.stderr.strip())
    return result.stdout.strip()


def _commit_configuration(repo: Path, parent: str, configuration: dict) -> None:
    _git(repo, "checkout", "--detach", parent)
    (repo / "configs" / "demo_runtime.json").write_text(json.dumps(configuration, sort_keys=True) + "\n")
    _git(repo, "add", "configs/demo_runtime.json")
    _git(repo, "commit", "-m", "fixture_configuration")


def _fixture_manipulation(before: dict, after: dict) -> dict:
    if before["depth_k_coupling"] != after["depth_k_coupling"]:
        raise ValueError("fixture_mechanism_changed")
    return {"depth_repair_fraction": (before["missing_columns"] - after["missing_columns"]) / 12,
            "phase_correction_turns": after["phase_correction_turns"] - before["phase_correction_turns"]}


def run_demo(output: Path) -> dict:
    output = output.resolve()
    source = Path(__file__).resolve().parents[2]
    if not (source / "pyproject.toml").is_file() or not (source / "configs" / "demo_runtime.json").is_file():
        raise ValueError("demo_requires_source_workspace")
    if output == source or source in output.parents:
        raise ValueError("demo_output_must_be_outside_source")
    if output.exists() and any(output.iterdir()):
        raise ValueError("demo_output_must_be_empty")
    output.mkdir(parents=True, exist_ok=True)
    repo = output / "code"
    shutil.copytree(
        source,
        repo,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            "*.egg-info",
            "venv",
            ".venv",
            "data",
            "runs",
            "evidence",
            "evaluator",
            "rst",
            "archive",
            "development_private",
            "segment-anything",
        ),
    )
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fresh_executable_fixture")
    store = CodeStore(repo, output / "archive")
    case = {"case_id": "synthetic_unseen", "scan_id": "synthetic_scan", "backend": "synthetic", "design_schema": "synthetic_design"}
    reference_case = dict(case, case_id="synthetic_expert", scan_id="synthetic_reference_scan")
    case_path = output / "inputs" / "case.json"
    reference_case_path = output / "inputs" / "reference_case.json"
    save_once(case_path, case)
    save_once(reference_case_path, reference_case)
    external_assets = {"case": file_digest(case_path), "reference_case": file_digest(reference_case_path)}
    baseline_revision = store.freeze(external_assets=external_assets)

    def execute(revision, label, source_path=case_path):
        run_dir = output / "runs" / label
        execution = store.execute(revision, (sys.executable, "-m", "rsi4tun", "fixture-run", "--case",
                                  str(source_path), "--config", "configs/demo_runtime.json", "--output", str(run_dir)), run_dir)
        if execution.returncode != 0:
            raise ValueError("fixture_execution_failed:" + Path(execution.stderr_path).read_text())
        run = run_from_dict(read_json(run_dir / "run.json"))
        if run.input_digest != digest(read_json(source_path)):
            raise ValueError("fixture_case_mismatch")
        return run, execution

    _commit_configuration(repo, baseline_revision.commit, {"missing_columns": 0, "phase_correction_turns": 0.1, "depth_k_coupling": 0.4})
    reference_revision = store.freeze(external_assets=external_assets)
    reference_run, _ = execute(reference_revision, "reference", reference_case_path)
    reference = replace(bundle_from_dict(read_json(Path(reference_run.artifact_path))),
                        source_role="expert_reference", expert_review_id="synthetic_review_only")
    reference_path = output / "evidence" / "reference.json"
    save_once(reference_path, reference)
    policy = ComparisonPolicy(0.1, ("synthetic_design",))
    contract = comparison_contract(reference, policy)
    proxy = FrozenProxy("synthetic_gate_fixture", ("depth_valid_coverage__delta", "k_phase_rms_turns__delta"),
                        (0.0, 0.0), (1.0, 1.0), (0.2, -1.0), 0.9, contract, "synthetic_fixture_only", "synthetic")
    save_once(output / "evaluator" / "proxy.json", proxy)
    save_once(output / "evaluator" / "policy.json", policy)
    external_assets.update({"reference": file_digest(reference_path), "proxy": file_digest(output / "evaluator" / "proxy.json"),
                            "policy": file_digest(output / "evaluator" / "policy.json")})
    _git(repo, "checkout", "--detach", baseline_revision.commit)
    baseline_revision = store.freeze(external_assets=external_assets)
    baseline_run, baseline_execution = execute(baseline_revision, "baseline")
    baseline = observe(baseline_run, reference, policy, proxy)
    comparison_path = output / "evidence" / "baseline_comparison.json"
    signal_path = output / "evidence" / "candidate_signals.json"
    save_once(comparison_path, baseline.comparison)
    signals = tuple(signal for signal in derive_signals(baseline.comparison, file_digest(Path(evidence.__file__)), digest(reference))
                    if signal.feature_id == "boundary_symmetric_distance_fraction__delta")
    save_once(signal_path, signals)
    candidate_proxy = propose_proxy(signals, digest(proxy))
    save_once(output / "evidence" / "candidate_proxy.json", candidate_proxy)
    baseline_evaluation = EvaluationReceipt("fixture_baseline", baseline_run.run_id, baseline_revision.commit,
                                           baseline_revision.tree, baseline_execution.digest, digest(proxy),
                                           digest(baseline.comparison), baseline.score is not None, None)
    store.promote(baseline_revision, baseline_evaluation)

    _commit_configuration(repo, baseline_revision.commit, {"missing_columns": 0, "phase_correction_turns": 0.0, "depth_k_coupling": 0.4})
    revision_a = store.freeze(external_assets=external_assets)
    _commit_configuration(repo, baseline_revision.commit, {"missing_columns": 3, "phase_correction_turns": 0.05, "depth_k_coupling": 0.4})
    revision_b = store.freeze(external_assets=external_assets)
    protected = ("src", "environment.lock.json", "configs/comparison.template.json", "configs/protocol.json")
    store.assert_unchanged(baseline_revision, revision_a, protected)
    store.assert_unchanged(baseline_revision, revision_b, protected)
    hypothesis_source = file_digest(Path(hypotheses.__file__))
    h1 = HypothesisProgram("depth_limits_k", "rsi4tun.hypotheses:depth_limits_k", hypothesis_source,
                           (("interval_half_width", 0.005), ("depth_to_k", 0.4), ("direct_phase_effect", 1.0)),
                           "dikw/knowledge/hypotheses/depth_vs_phase.md")
    h2 = HypothesisProgram("phase_limits_k", "rsi4tun.hypotheses:phase_limits_k", hypothesis_source,
                           (("interval_half_width", 0.005), ("incidental_depth_effect", 0.0), ("phase_to_k", 1.0)),
                           "dikw/knowledge/hypotheses/depth_vs_phase.md")
    arms = (Arm("A", revision_a.commit, revision_a.tree, (("depth_repair_fraction", 0.25),)),
            Arm("B", revision_b.commit, revision_b.tree, (("phase_correction_turns", 0.05),)))
    plan = build_plan(experiment_id="synthetic_depth_vs_phase", baseline_run_id=baseline_run.run_id,
                      baseline_commit=baseline_revision.commit, comparison=baseline.comparison,
                      candidate_signals=signals, proxy_digest=digest(proxy), evidence_contract_digest=contract,
                      arms=arms, hypotheses=(h1, h2),
                      thresholds=(("depth_valid_coverage__delta", 0.01), ("k_phase_rms_turns__delta", 0.01),
                                  ("boundary_symmetric_distance_fraction__delta", 0.005)),
                      units=(("depth_valid_coverage__delta", "fraction"), ("k_phase_rms_turns__delta", "turns"),
                             ("boundary_symmetric_distance_fraction__delta", "circumference_fraction")),
                      manipulation_intervals=(("A", "depth_repair_fraction", 0.24, 0.26),
                                              ("B", "phase_correction_turns", 0.04, 0.06)),
                      knowledge_ref="dikw/knowledge/research_notes/synthetic_example.md", candidate_proxy=candidate_proxy)
    arm_outputs = (output / "runs" / "arm_a", output / "runs" / "arm_b")
    commands = tuple((sys.executable, "-m", "rsi4tun", "fixture-run", "--case", str(case_path),
                      "--config", "configs/demo_runtime.json", "--output", str(path)) for path in arm_outputs)
    before_path, before_digest, observations, executions, diagnosis = preregister_and_execute(
        store=store, baseline_revision=baseline_revision, baseline=baseline, plan=plan,
        revisions=(revision_a, revision_b), commands=commands, output_dirs=arm_outputs,
        record_root=output / "rst", campaign_id="synthetic_only", synthetic=True,
        comparison_path=comparison_path, signal_path=signal_path, reference=reference,
        policy=policy, proxy=proxy, manipulation_reader=_fixture_manipulation)
    observation_a, observation_b = observations
    run_a, run_b = observation_a.run, observation_b.run
    execution_a = executions[0]
    decision_a = decide_treatment(baseline, observation_a, epsilon=1e-6, operator_digest=digest(arms[0]))
    decision_b = decide_treatment(baseline, observation_b, epsilon=1e-6, operator_digest=digest(arms[1]))
    if decision_a.status != "retain" or observation_a.score <= observation_b.score:
        raise ValueError("fixture_selection_failed")
    accepted_evaluation = EvaluationReceipt(plan.experiment_id, run_a.run_id, revision_a.commit, revision_a.tree,
                                           execution_a.digest, digest(proxy), digest(observation_a.comparison),
                                           decision_a.status == "retain", store.accepted_commit())
    accepted_release = store.promote(revision_a, accepted_evaluation)
    outcome_path = append_outcome(before_path, before_digest, plan, diagnosis=diagnosis,
                                 run_ids=(run_a.run_id, run_b.run_id), code_commits=(revision_a.commit, revision_b.commit),
                                 treatment_decisions=({**asdict(decision_a), "activated": True},
                                                      {**asdict(decision_b), "activated": False}),
                                 next_action="submit_comparison_signal_and_response_to_development",
                                 knowledge_ref="dikw/knowledge/research_notes/synthetic_example.md")

    _commit_configuration(repo, revision_a.commit, {"missing_columns": 6, "phase_correction_turns": 0.0, "depth_k_coupling": 0.4})
    rejected_revision = store.freeze(external_assets=external_assets)
    store.assert_unchanged(revision_a, rejected_revision, protected)
    rejected_run, _ = execute(rejected_revision, "rejected_followup")
    rejected = observe(rejected_run, reference, policy, proxy)
    rollback = decide_treatment(observation_a, rejected, epsilon=1e-6, operator_digest=digest({"missing_columns": 6}))
    save_once(output / "rst" / "warning.json", {"synthetic": True, "learning_eligible": False, "decision": asdict(rollback),
                                               "accepted_commit": store.accepted_commit(), "sent": False})
    repeated_run, _ = execute(revision_a, "plateau_repeat")
    repeated = observe(repeated_run, reference, policy, proxy)
    plateau = decide_treatment(observation_a, repeated, epsilon=1e-6, operator_digest=digest({"repeat": revision_a.commit}))
    save_once(output / "rst" / "plateau.json", {"synthetic": True, "learning_eligible": False, "decision": asdict(plateau)})

    from rsi4tun.evaluation import evaluate_miou
    truth = {point: (point % 12) // 3 for point in baseline_run.point_ids}
    private_audit = {run.run_id: asdict(evaluate_miou(run, truth, class_ids=(0, 1, 2, 3)))
                     for run in (baseline_run, run_a, run_b, rejected_run)}
    save_once(output / "development_private" / "posthoc_fixture_audit.json", private_audit)
    report = {
        "synthetic": True,
        "learning_eligible": False,
        "real_sam_executed": False,
        "comparison_before_diagnosis": True,
        "full_pipeline_runs": 6,
        "baseline_score": baseline.score,
        "arm_a_score": observation_a.score,
        "arm_b_score": observation_b.score,
        "diagnosis": diagnosis["status"],
        "causal_status": "unconfirmed",
        "accepted_commit": accepted_release.commit,
        "accepted_tree": accepted_release.tree,
        "accepted_bundle": revision_a.bundle_path,
        "rollback_status": rollback.status,
        "rollback_preserved_accepted_commit": store.accepted_commit() == revision_a.commit,
        "plateau_status": plateau.status,
        "rst_before": str(before_path),
        "rst_after": str(outcome_path),
        "new_proxy_development_validation": "not_performed_by_fixture",
        "scientific_knowledge_promoted": False,
    }
    save_once(output / "report.json", report)
    return report
