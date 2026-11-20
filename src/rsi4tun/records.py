from dataclasses import asdict
from pathlib import Path

from rsi4tun.contracts import PROTOCOL, digest, read_json, save_once
from rsi4tun.diagnosis import ExperimentPlan, classify_responses


FORBIDDEN_DEPLOYMENT_KEYS = frozenset(("ground_truth", "truth_by_point", "final_miou", "gt_labels", "miou", "target_miou"))


def require_gt_free(value) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_DEPLOYMENT_KEYS.intersection(value):
            raise ValueError("private_development_field")
        for child in value.values():
            require_gt_free(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            require_gt_free(child)


def preregister(root: Path, plan: ExperimentPlan, *, campaign_id: str, synthetic: bool,
                comparison_path: str, signal_path: str, retrieved_claim_ids: tuple[str, ...] = ()) -> tuple[Path, str]:
    if type(synthetic) is not bool or not campaign_id:
        raise ValueError("invalid_record_identity")
    if digest(read_json(Path(comparison_path))) != plan.comparison_digest:
        raise ValueError("comparison_record_mismatch")
    if digest(read_json(Path(signal_path))) != plan.candidate_signal_digest:
        raise ValueError("signal_record_mismatch")
    record = {
        "schema": PROTOCOL,
        "event": "rst_before",
        "campaign_id": campaign_id,
        "synthetic": synthetic,
        "learning_eligible": not synthetic,
        "plan": asdict(plan),
        "plan_digest": digest(plan),
        "comparison_path": comparison_path,
        "signal_path": signal_path,
        "retrieved_claim_ids": retrieved_claim_ids,
    }
    require_gt_free(record)
    path = root / (plan.experiment_id + ".before.json")
    return path, save_once(path, record)


def verify_preregistration(path: Path, expected_digest: str, plan: ExperimentPlan) -> dict:
    record = read_json(path)
    if digest(record) != expected_digest or record["plan_digest"] != digest(plan):
        raise ValueError("preregistration_integrity_failure")
    if digest(record["plan"]) != digest(plan):
        raise ValueError("plan_changed_after_registration")
    if digest(read_json(Path(record["comparison_path"]))) != plan.comparison_digest:
        raise ValueError("comparison_record_changed")
    if digest(read_json(Path(record["signal_path"]))) != plan.candidate_signal_digest:
        raise ValueError("signal_record_changed")
    return record


def append_outcome(path: Path, before_digest: str, plan: ExperimentPlan, *,
                   diagnosis: dict, run_ids: tuple[str, ...], code_commits: tuple[str, ...],
                   treatment_decisions: tuple[dict, ...], next_action: str,
                   knowledge_ref: str) -> Path:
    before = verify_preregistration(path, before_digest, plan)
    if diagnosis["plan_digest"] != digest(plan):
        raise ValueError("diagnosis_plan_mismatch")
    if digest(classify_responses(plan, diagnosis["responses"], diagnosis["actual_interventions"])) != digest(diagnosis):
        raise ValueError("diagnosis_response_contradiction")
    if not knowledge_ref.startswith("dikw/knowledge/"):
        raise ValueError("record_description_location")
    if code_commits != tuple(arm.code_commit for arm in plan.arms) or len(run_ids) != len(plan.arms):
        raise ValueError("experiment_revision_mismatch")
    record = {
        "schema": PROTOCOL,
        "event": "rst_after",
        "campaign_id": before["campaign_id"],
        "synthetic": before["synthetic"],
        "learning_eligible": before["learning_eligible"],
        "before_digest": before_digest,
        "plan_digest": digest(plan),
        "diagnosis": diagnosis,
        "run_ids": run_ids,
        "code_commits": code_commits,
        "treatment_decisions": treatment_decisions,
        "next_action": next_action,
        "knowledge_ref": knowledge_ref,
    }
    require_gt_free(record)
    target = path.with_name(plan.experiment_id + ".after.json")
    save_once(target, record)
    return target


def assess_knowledge_promotion(request: dict, evidence: tuple[dict, ...], tests: tuple[dict, ...]) -> dict:
    required = ("claim_id", "claim_kind", "scope_id", "assumptions_ref", "counterexamples_ref", "code_commit", "knowledge_ref")
    if any(not request.get(key) for key in required):
        raise ValueError("incomplete_knowledge_request")
    if request["claim_kind"] not in ("measurement_contract", "statistical_association", "scoped_intervention_response"):
        raise ValueError("unsupported_claim_kind")
    if not evidence or not tests:
        decision = "pending_evidence"
    elif any(item.get("synthetic") is not False or item.get("learning_eligible") is not True for item in evidence):
        decision = "reject_fixture_or_ineligible_evidence"
    elif any(item.get("passed") is not True or not item.get("test_code_digest") or not item.get("evidence_digest")
             or item.get("claim_id") != request["claim_id"] or item.get("code_commit") != request["code_commit"] for item in tests):
        decision = "pending_executable_support"
    else:
        allowed = {digest(item) for item in evidence}
        decision = "eligible_for_scoped_review" if all(item["evidence_digest"] in allowed for item in tests) else "evidence_binding_failure"
    return {"claim_id": request["claim_id"], "decision": decision, "request_digest": digest(request),
            "evidence_digests": tuple(digest(item) for item in evidence), "test_digests": tuple(digest(item) for item in tests)}


def retrieve_claims(registry: tuple[dict, ...], scope_id: str) -> tuple[dict, ...]:
    eligible = [item for item in registry if item.get("status") == "accepted"
                and item.get("scope_id") == scope_id and item.get("synthetic") is False
                and item.get("evidence_digests") and item.get("test_digests")]
    knowledge = [item for item in eligible if item.get("level") == "knowledge"]
    knowledge_ids = {item["claim_id"] for item in knowledge}
    wisdom = [item for item in eligible if item.get("level") == "wisdom" and item.get("knowledge_ids")
              and set(item["knowledge_ids"]) <= knowledge_ids]
    return tuple(wisdom + knowledge)
