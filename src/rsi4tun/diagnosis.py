from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Mapping

from rsi4tun.contracts import OBJECTIVE, digest, file_digest, finite
from rsi4tun.proxy import ProxyProposal, propose_proxy


@dataclass(frozen=True)
class HypothesisProgram:
    hypothesis_id: str
    entrypoint: str
    source_sha256: str
    parameters: tuple[tuple[str, float], ...]
    knowledge_ref: str

    def predict(self, baseline: Mapping, interventions: Mapping) -> dict:
        if not self.knowledge_ref.startswith("knowledge/"):
            raise ValueError("hypothesis_description_location")
        module_name, function_name = self.entrypoint.split(":", 1)
        if module_name != "rsi4tun.hypotheses":
            raise ValueError("hypothesis_module_not_registered")
        module = importlib.import_module(module_name)
        if file_digest(Path(module.__file__)) != self.source_sha256:
            raise ValueError("hypothesis_code_changed")
        result = getattr(module, function_name)(baseline, interventions, dict(self.parameters))
        if set(result) != set(interventions):
            raise ValueError("hypotheses_must_predict_same_interventions")
        for outcomes in result.values():
            for interval in outcomes.values():
                if len(interval) != 2 or finite(interval[0]) > finite(interval[1]):
                    raise ValueError("invalid_prediction_interval")
        return result


@dataclass(frozen=True)
class Arm:
    arm_id: str
    code_commit: str
    code_tree: str
    intervention_vector: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class ExperimentPlan:
    experiment_id: str
    baseline_run_id: str
    baseline_commit: str
    comparison_digest: str
    candidate_signal_digest: str
    proxy_digest: str
    evidence_contract_digest: str
    arms: tuple[Arm, ...]
    hypotheses: tuple[HypothesisProgram, HypothesisProgram]
    predictions: tuple[dict, dict]
    thresholds: tuple[tuple[str, float], ...]
    units: tuple[tuple[str, str], ...]
    manipulation_intervals: tuple[tuple[str, str, float, float], ...]
    knowledge_ref: str
    candidate_proxy_digest: str = ""


def build_plan(*, experiment_id: str, baseline_run_id: str, baseline_commit: str,
               comparison: dict, candidate_signals: tuple, proxy_digest: str,
               evidence_contract_digest: str, arms: tuple[Arm, ...],
               hypotheses: tuple[HypothesisProgram, HypothesisProgram],
               thresholds: tuple[tuple[str, float], ...], units: tuple[tuple[str, str], ...],
               manipulation_intervals: tuple[tuple[str, str, float, float], ...],
               knowledge_ref: str, candidate_proxy: ProxyProposal | None = None) -> ExperimentPlan:
    if not arms or len({arm.arm_id for arm in arms}) != len(arms):
        raise ValueError("invalid_experiment_arms")
    if comparison["status"] not in ("comparable", "partial") or not candidate_signals:
        raise ValueError("comparison_required_before_diagnosis")
    if any(signal.comparison_digest != digest(comparison) for signal in candidate_signals):
        raise ValueError("signals_from_different_evidence")
    signal_names = [signal.feature_id for signal in candidate_signals]
    if len(set(signal_names)) != len(signal_names) or any(name not in comparison["features"] for name in signal_names):
        raise ValueError("candidate_signal_not_measured")
    if any(signal.target != OBJECTIVE or signal.status != "unvalidated" for signal in candidate_signals):
        raise ValueError("invalid_candidate_signal_status")
    expected_proposal = propose_proxy(candidate_signals, proxy_digest)
    candidate_proxy = candidate_proxy or expected_proposal
    if digest(candidate_proxy) != digest(expected_proposal):
        raise ValueError("candidate_proxy_not_derived_from_comparison")
    if len(hypotheses) != 2 or hypotheses[0].hypothesis_id == hypotheses[1].hypothesis_id:
        raise ValueError("two_distinct_hypotheses_required")
    if not knowledge_ref.startswith("knowledge/"):
        raise ValueError("experiment_description_location")
    interventions = {arm.arm_id: dict(arm.intervention_vector) for arm in arms}
    predictions = tuple(hypothesis.predict(comparison["features"], interventions) for hypothesis in hypotheses)
    threshold_map = dict(thresholds)
    unit_map = dict(units)
    dimensions = set()
    for arm in arms:
        first, second = predictions[0][arm.arm_id], predictions[1][arm.arm_id]
        if set(first) != set(second) or not first:
            raise ValueError("prediction_observables_mismatch")
        dimensions.update(first)
    if set(threshold_map) != dimensions or set(unit_map) != dimensions:
        raise ValueError("missing_metric_units_or_noise")
    if not set(signal_names) <= dimensions:
        raise ValueError("candidate_signal_not_predicted")
    if not dimensions <= set(comparison["features"]):
        raise ValueError("prediction_metric_not_measured")
    if len(threshold_map) != len(thresholds) or len(unit_map) != len(units) or any(not value for value in unit_map.values()):
        raise ValueError("invalid_metric_units_or_noise")
    if any(finite(value) <= 0 for value in threshold_map.values()):
        raise ValueError("invalid_response_threshold")
    separated = False
    for arm in arms:
        for metric in predictions[0][arm.arm_id]:
            first = predictions[0][arm.arm_id][metric]
            second = predictions[1][arm.arm_id][metric]
            gap = max(second[0] - first[1], first[0] - second[1])
            separated = separated or gap > threshold_map[metric]
    if not separated:
        raise ValueError("predictions_not_distinguishable")
    covered = {name for name, _, _, _ in manipulation_intervals}
    if covered != set(interventions):
        raise ValueError("missing_manipulation_checks")
    for name, metric, lower, upper in manipulation_intervals:
        if metric not in interventions[name] or finite(lower) > finite(upper):
            raise ValueError("invalid_manipulation_check")
    return ExperimentPlan(experiment_id, baseline_run_id, baseline_commit, digest(comparison),
                          digest(candidate_signals), proxy_digest, evidence_contract_digest, arms,
                          hypotheses, predictions, thresholds, units, manipulation_intervals, knowledge_ref, digest(candidate_proxy))


def evaluate_plan(plan: ExperimentPlan, baseline_features: Mapping,
                  arm_features: Mapping[str, Mapping[str, float]], actual_interventions: dict) -> dict:
    if set(arm_features) != {arm.arm_id for arm in plan.arms}:
        raise ValueError("missing_experiment_arm")
    responses = {}
    for arm in plan.arms:
        responses[arm.arm_id] = {
            metric: finite(finite(arm_features[arm.arm_id][metric]) - finite(baseline_features[metric]))
            for metric, _ in plan.thresholds
        }
    return classify_responses(plan, responses, actual_interventions)


def classify_responses(plan: ExperimentPlan, responses: dict, actual_interventions: dict) -> dict:
    if set(responses) != {arm.arm_id for arm in plan.arms}:
        raise ValueError("response_arm_mismatch")
    for values in responses.values():
        if set(values) != {metric for metric, _ in plan.thresholds}:
            raise ValueError("response_metric_mismatch")
        for value in values.values():
            finite(value)
    if set(actual_interventions) != set(responses):
        raise ValueError("intervention_receipt_mismatch")
    manipulation = all(lower <= finite(actual_interventions[name][metric]) <= upper
                       for name, metric, lower, upper in plan.manipulation_intervals)
    matches = tuple(all(lower <= responses[arm][metric] <= upper
                        for arm, metrics in prediction.items() for metric, (lower, upper) in metrics.items())
                    for prediction in plan.predictions)
    responsive = any(abs(value) > dict(plan.thresholds)[metric]
                     for metrics in responses.values() for metric, value in metrics.items())
    if not manipulation:
        status = "invalid_manipulation"
    elif matches == (True, False):
        status = "h1_supported"
    elif matches == (False, True):
        status = "h2_supported"
    elif matches == (True, True):
        status = "both_compatible"
    else:
        status = "neither_supported"
    return {
        "plan_digest": digest(plan),
        "status": status,
        "matches": matches,
        "responses": responses,
        "actual_interventions": actual_interventions,
        "manipulation_valid": manipulation,
        "response_above_noise": responsive,
        "causal_status": "unconfirmed",
        "candidate_validation_status": "development_required",
    }
