from dataclasses import asdict, dataclass
from pathlib import Path
import json

from rsi4tun.contracts import CompletedRun, digest, file_digest, finite, read_json, run_from_dict
from rsi4tun.diagnosis import ExperimentPlan, evaluate_plan
from rsi4tun.evidence import ArtifactBundle, ComparisonPolicy, assert_fixed_evidence, bundle_from_dict, compare_reference
from rsi4tun.proxy import FrozenProxy
from rsi4tun.records import preregister, verify_preregistration
from rsi4tun.versions import CodeStore, ExecutionReceipt, Revision


@dataclass(frozen=True)
class Observation:
    run: CompletedRun
    comparison: dict
    proxy_digest: str
    evidence_contract_digest: str
    score: float | None


@dataclass(frozen=True)
class TreatmentDecision:
    status: str
    baseline_run_id: str
    candidate_run_id: str
    baseline_commit: str
    candidate_commit: str
    proxy_digest: str
    score_change: float | None
    warning_key: str | None


def comparison_contract(reference: ArtifactBundle, policy: ComparisonPolicy) -> str:
    from rsi4tun import evidence
    return digest({"reference": asdict(reference), "policy": asdict(policy),
                   "extractor_code": file_digest(Path(evidence.__file__))})


def observe(run: CompletedRun, reference: ArtifactBundle, policy: ComparisonPolicy,
            proxy: FrozenProxy) -> Observation:
    run.require_complete()
    bundle = bundle_from_dict(read_json(Path(run.artifact_path)))
    if (bundle.case_id, bundle.code_commit, bundle.backend) != (run.case_id, run.code_commit, run.backend):
        raise ValueError("artifact_run_provenance_mismatch")
    contract = comparison_contract(reference, policy)
    report = asdict(compare_reference(reference, bundle, policy))
    score = None
    if report["status"] in ("comparable", "partial"):
        try:
            score = proxy.score(report["features"], contract, run.backend)
        except ValueError as error:
            if str(error) != "proxy_feature_unavailable":
                raise
    return Observation(run, report, digest(proxy), contract, score)


def decide_treatment(baseline: Observation, candidate: Observation, *, epsilon: float,
                     operator_digest: str) -> TreatmentDecision:
    if finite(epsilon) < 0:
        raise ValueError("invalid_score_tolerance")
    if (baseline.proxy_digest, baseline.evidence_contract_digest) != (candidate.proxy_digest, candidate.evidence_contract_digest):
        raise ValueError("incomparable_evaluators")
    if (baseline.run.case_id, baseline.run.input_digest, baseline.run.point_ids) != (candidate.run.case_id, candidate.run.input_digest, candidate.run.point_ids):
        raise ValueError("incomparable_cases")
    baseline.run.require_complete()
    candidate.run.require_complete()
    assert_fixed_evidence(bundle_from_dict(read_json(Path(baseline.run.artifact_path))),
                          bundle_from_dict(read_json(Path(candidate.run.artifact_path))))
    delta = None if baseline.score is None or candidate.score is None else finite(finite(candidate.score) - finite(baseline.score))
    if delta is None:
        status = "abstain"
    elif delta > epsilon:
        status = "retain"
    elif delta < -epsilon:
        status = "rollback"
    else:
        status = "plateau"
    warning = None
    if status == "rollback":
        warning = digest({"case": baseline.run.input_digest, "baseline_commit": baseline.run.code_commit,
                          "evaluator": baseline.proxy_digest, "contract": baseline.evidence_contract_digest,
                          "operator": operator_digest})
    return TreatmentDecision(status, baseline.run.run_id, candidate.run.run_id,
                             baseline.run.code_commit, candidate.run.code_commit,
                             baseline.proxy_digest, delta, warning)


def analyse_experiment(plan: ExperimentPlan, registration_path: Path, registration_digest: str,
                       baseline: Observation, arms: tuple[Observation, ...],
                       execution_receipts: tuple[ExecutionReceipt, ...], actual_interventions: dict) -> dict:
    verify_preregistration(registration_path, registration_digest, plan)
    if (baseline.run.run_id, baseline.run.code_commit, digest(baseline.comparison), baseline.proxy_digest,
        baseline.evidence_contract_digest) != (plan.baseline_run_id, plan.baseline_commit,
        plan.comparison_digest, plan.proxy_digest, plan.evidence_contract_digest):
        raise ValueError("experiment_baseline_mismatch")
    if len(arms) != len(plan.arms) or len(execution_receipts) != len(plan.arms):
        raise ValueError("missing_experiment_arm")
    arm_features = {}
    baseline_bundle = bundle_from_dict(read_json(Path(baseline.run.artifact_path)))
    for arm, observed, execution in zip(plan.arms, arms, execution_receipts):
        if (execution.registration_digest, execution.registration_path, execution.revision_commit) != (
            registration_digest, str(registration_path), arm.code_commit):
            raise ValueError("execution_not_preregistered")
        observed.run.require_complete()
        if (observed.run.code_commit, observed.run.code_tree) != (arm.code_commit, arm.code_tree):
            raise ValueError("experiment_code_mismatch")
        if (observed.run.input_digest, observed.proxy_digest, observed.evidence_contract_digest) != (
            baseline.run.input_digest, plan.proxy_digest, plan.evidence_contract_digest):
            raise ValueError("experiment_control_mismatch")
        if observed.comparison["status"] not in ("comparable", "partial"):
            raise ValueError("experiment_measurement_unavailable")
        assert_fixed_evidence(baseline_bundle, bundle_from_dict(read_json(Path(observed.run.artifact_path))))
        arm_features[arm.arm_id] = observed.comparison["features"]
    result = evaluate_plan(plan, baseline.comparison["features"], arm_features, actual_interventions)
    verify_preregistration(registration_path, registration_digest, plan)
    return result


def preregister_and_execute(*, store: CodeStore, baseline_revision: Revision, baseline: Observation,
                            plan: ExperimentPlan, revisions: tuple[Revision, ...], commands: tuple[tuple[str, ...], ...],
                            output_dirs: tuple[Path, ...], record_root: Path, campaign_id: str, synthetic: bool,
                            comparison_path: Path, signal_path: Path, reference: ArtifactBundle,
                            policy: ComparisonPolicy, proxy: FrozenProxy, manipulation_reader,
                            configuration_path: str = "configs/demo_runtime.json") -> tuple:
    if len({len(plan.arms), len(revisions), len(commands), len(output_dirs)}) != 1:
        raise ValueError("incomplete_execution_plan")
    if any(path.exists() for path in output_dirs):
        raise ValueError("experiment_outputs_already_exist")
    if baseline_revision.commit != plan.baseline_commit:
        raise ValueError("registered_baseline_revision_mismatch")
    protected = ("src/rsi4tun/evidence.py", "src/rsi4tun/proxy.py", "src/rsi4tun/contracts.py",
                 "src/rsi4tun/diagnosis.py", "src/rsi4tun/hypotheses.py", "src/rsi4tun/records.py",
                 "src/rsi4tun/orchestrator.py", "src/rsi4tun/versions.py", "src/rsi4tun/cli.py",
                 "environment.lock.json", "configs/protocol.json", "configs/comparison.template.json")
    for arm, revision in zip(plan.arms, revisions):
        if (revision.commit, revision.tree) != (arm.code_commit, arm.code_tree):
            raise ValueError("planned_revision_mismatch")
        store.assert_unchanged(baseline_revision, revision, protected)
    path, registration_digest = preregister(record_root, plan, campaign_id=campaign_id, synthetic=synthetic,
                                           comparison_path=str(comparison_path), signal_path=str(signal_path))
    observed, executions, actual_interventions = [], [], {}
    base_configuration = json.loads(store.read_revision_file(baseline_revision, configuration_path))
    for arm, revision, command, output_dir in zip(plan.arms, revisions, commands, output_dirs):
        verify_preregistration(path, registration_digest, plan)
        execution = store.execute(revision, command, output_dir, registration=(path, registration_digest))
        store.verify_execution(revision, execution.digest)
        run = run_from_dict(read_json(output_dir / "run.json"))
        configuration = json.loads(store.read_revision_file(revision, configuration_path))
        applied_digest = read_json(Path(run.artifact_path).parent / "stages" / "unfolding.json")["configuration_digest"]
        if applied_digest != digest(configuration):
            raise ValueError("runtime_configuration_differs_from_snapshot")
        actual_interventions[arm.arm_id] = manipulation_reader(base_configuration, configuration)
        observed.append(observe(run, reference, policy, proxy))
        executions.append(execution)
    diagnosis = analyse_experiment(plan, path, registration_digest, baseline, tuple(observed), tuple(executions), actual_interventions)
    return path, registration_digest, tuple(observed), tuple(executions), diagnosis


def coverage_action(report: dict, existing_matching_development_cases: int, budget_available: bool) -> str:
    if report["status"] not in ("coverage_gap", "insufficient_reference"):
        return "investigate_measurement_or_hypotheses"
    if existing_matching_development_cases > 0:
        return "evaluate_existing_labelled_coverage"
    return "request_one_representative_labelled_subset" if budget_available else "defer_unsupported_scope"
