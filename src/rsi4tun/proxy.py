from dataclasses import dataclass, replace
from statistics import mean
from typing import Mapping

from rsi4tun.contracts import OBJECTIVE, digest, finite


@dataclass(frozen=True)
class CandidateSignal:
    feature_id: str
    comparison_digest: str
    extractor_digest: str
    reference_digest: str
    target: str = OBJECTIVE
    status: str = "unvalidated"


def derive_signals(report: Mapping, extractor_digest: str, reference_digest: str) -> tuple[CandidateSignal, ...]:
    if report["status"] not in ("comparable", "partial"):
        return ()
    features = dict(report["features"])
    for value in features.values():
        finite(value)
    return tuple(CandidateSignal(key, digest(report), extractor_digest, reference_digest) for key in sorted(features))


@dataclass(frozen=True)
class ProxyProposal:
    incumbent_proxy_digest: str
    comparison_digest: str
    candidate_signal_digest: str
    added_features: tuple[str, ...]
    composition: str = "retain_incumbent_features_and_append"
    estimator: str = "standardised_ridge"
    target: str = OBJECTIVE
    status: str = "development_validation_required"


def propose_proxy(signals: tuple[CandidateSignal, ...], incumbent_proxy_digest: str) -> ProxyProposal:
    if not signals or len({signal.comparison_digest for signal in signals}) != 1 or not incumbent_proxy_digest:
        raise ValueError("invalid_proxy_proposal_evidence")
    names = tuple(signal.feature_id for signal in signals)
    if len(names) != len(set(names)) or any(signal.target != OBJECTIVE or signal.status != "unvalidated" for signal in signals):
        raise ValueError("invalid_proxy_proposal_signals")
    return ProxyProposal(incumbent_proxy_digest, signals[0].comparison_digest, digest(signals), names)


@dataclass(frozen=True)
class FrozenProxy:
    proxy_id: str
    feature_ids: tuple[str, ...]
    centres: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    intercept: float
    evidence_contract_digest: str
    validation_receipt: str
    backend: str
    target: str = OBJECTIVE
    fit_rows_digest: str = ""
    fit_case_ids: tuple[str, ...] = ()
    fit_group_ids: tuple[str, ...] = ()

    def score(self, features: Mapping[str, float], contract_digest: str, backend: str) -> float:
        if self.validation_receipt in ("", "development_fit_pending"):
            raise ValueError("unvalidated_proxy")
        return self.predict(features, contract_digest, backend)

    def predict(self, features: Mapping[str, float], contract_digest: str, backend: str) -> float:
        if self.target != OBJECTIVE:
            raise ValueError("invalid_proxy_target")
        if self.evidence_contract_digest != contract_digest or self.backend != backend:
            raise ValueError("proxy_contract_mismatch")
        if not self.feature_ids or len(set(self.feature_ids)) != len(self.feature_ids):
            raise ValueError("invalid_proxy_features")
        if len({len(self.feature_ids), len(self.centres), len(self.scales), len(self.weights)}) != 1:
            raise ValueError("invalid_proxy_shape")
        result = finite(self.intercept)
        for key, centre, scale, weight in zip(self.feature_ids, self.centres, self.scales, self.weights):
            if key not in features or finite(scale) <= 0:
                raise ValueError("proxy_feature_unavailable")
            result = finite(result + finite(weight) * (finite(features[key]) - finite(centre)) / scale)
        return max(0.0, min(1.0, finite(result)))


@dataclass(frozen=True)
class DevelopmentRow:
    case_id: str
    group_id: str
    run_id: str
    features: tuple[tuple[str, float], ...]
    final_miou: float
    is_baseline: bool = False


@dataclass(frozen=True)
class ValidationPolicy:
    minimum_heldout_groups: int = 2
    maximum_mae_drop: float = 0.0
    minimum_selection_gain: float = 0.0
    maximum_group_drop: float = 0.0
    minimum_weight: float = 1e-8


@dataclass(frozen=True)
class ProxyValidation:
    decision: str
    old_mae: float | None
    new_mae: float
    selection_gain: float | None
    worst_group_change: float | None
    heldout_groups: tuple[str, ...]
    candidate_proxy_digest: str
    evidence_digest: str
    policy_digest: str
    incumbent_proxy_digest: str | None = None


def _validate_rows(rows: tuple[DevelopmentRow, ...]) -> None:
    run_ids = set()
    groups_by_case = {}
    for row in rows:
        if any(not isinstance(value, str) or not value.strip() for value in (row.case_id, row.group_id, row.run_id)):
            raise ValueError("missing_development_identity")
        if row.run_id in run_ids:
            raise ValueError("duplicate_development_run")
        run_ids.add(row.run_id)
        if row.case_id in groups_by_case and groups_by_case[row.case_id] != row.group_id:
            raise ValueError("inconsistent_case_group")
        groups_by_case[row.case_id] = row.group_id
        keys = [key for key, _ in row.features]
        if not keys or len(keys) != len(set(keys)) or any(not isinstance(key, str) or not key for key in keys):
            raise ValueError("invalid_development_features")
        for _, value in row.features:
            finite(value)
        if not 0 <= finite(row.final_miou) <= 1:
            raise ValueError("invalid_miou")
        if type(row.is_baseline) is not bool:
            raise ValueError("invalid_baseline_flag")


def _solve(matrix: list[list[float]], target: list[float]) -> list[float]:
    augmented = [row[:] + [value] for row, value in zip(matrix, target)]
    size = len(target)
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("singular_development_design")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [value / scale for value in augmented[col]]
        for row in range(size):
            if row != col:
                scale = augmented[row][col]
                augmented[row] = [a - scale * b for a, b in zip(augmented[row], augmented[col])]
    return [row[-1] for row in augmented]


def fit_proxy(rows: tuple[DevelopmentRow, ...], feature_ids: tuple[str, ...], *, proxy_id: str,
              evidence_contract_digest: str, backend: str, ridge: float = 1e-3) -> FrozenProxy:
    if not rows or not feature_ids or len(set(feature_ids)) != len(feature_ids) or finite(ridge) <= 0:
        raise ValueError("invalid_fit_request")
    _validate_rows(rows)
    if any(not isinstance(key, str) or not key for key in feature_ids):
        raise ValueError("invalid_fit_features")
    if any(key not in dict(row.features) for row in rows for key in feature_ids):
        raise ValueError("missing_fit_feature")
    if not proxy_id or not evidence_contract_digest or not backend:
        raise ValueError("missing_fit_provenance")
    columns = [[finite(dict(row.features)[key]) for row in rows] for key in feature_ids]
    targets = [finite(row.final_miou) for row in rows]
    if any(value < 0 or value > 1 for value in targets):
        raise ValueError("invalid_miou")
    centres = tuple(finite(mean(column)) for column in columns)
    scales = tuple(max(finite(mean(finite((value - centre) * (value - centre)) for value in column)) ** 0.5, 1e-8)
                   for column, centre in zip(columns, centres))
    design = [[1.0] + [(column[i] - centre) / scale for column, centre, scale in zip(columns, centres, scales)]
              for i in range(len(rows))]
    size = len(feature_ids) + 1
    matrix = [[sum(row[i] * row[j] for row in design) + (ridge if i == j and i else 0.0)
               for j in range(size)] for i in range(size)]
    target = [sum(row[i] * value for row, value in zip(design, targets)) for i in range(size)]
    solution = _solve(matrix, target)
    return FrozenProxy(proxy_id, feature_ids, centres, scales, tuple(finite(value) for value in solution[1:]), finite(solution[0]),
                       evidence_contract_digest, "development_fit_pending", backend, fit_rows_digest=digest(rows),
                       fit_case_ids=tuple(sorted({row.case_id for row in rows})),
                       fit_group_ids=tuple(sorted({row.group_id for row in rows})))


def validate_proxy(candidate: FrozenProxy, incumbent: FrozenProxy | None,
                   training_rows: tuple[DevelopmentRow, ...], heldout_rows: tuple[DevelopmentRow, ...],
                   new_feature_ids: tuple[str, ...], policy: ValidationPolicy) -> ProxyValidation:
    if any(finite(value) < 0 for value in (policy.maximum_mae_drop, policy.minimum_selection_gain,
                                          policy.maximum_group_drop, policy.minimum_weight)):
        raise ValueError("invalid_validation_tolerance")
    if type(policy.minimum_heldout_groups) is not int or policy.minimum_heldout_groups < 2 or not heldout_rows or not training_rows:
        raise ValueError("insufficient_grouped_validation")
    _validate_rows(training_rows + heldout_rows)
    train_groups = {row.group_id for row in training_rows}
    heldout_groups = {row.group_id for row in heldout_rows}
    train_cases = {row.case_id for row in training_rows}
    heldout_cases = {row.case_id for row in heldout_rows}
    if train_groups & heldout_groups or train_cases & heldout_cases:
        raise ValueError("development_split_leakage")
    if candidate.fit_rows_digest != digest(training_rows) or candidate.fit_case_ids != tuple(sorted(train_cases)) or candidate.fit_group_ids != tuple(sorted(train_groups)):
        raise ValueError("fit_provenance_mismatch")
    if not new_feature_ids or len(new_feature_ids) != len(set(new_feature_ids)) or any(key not in candidate.feature_ids for key in new_feature_ids):
        raise ValueError("missing_candidate_features")
    if incumbent and (candidate.evidence_contract_digest != incumbent.evidence_contract_digest
                      or candidate.backend != incumbent.backend):
        raise ValueError("incomparable_proxy_contracts")
    if incumbent and not set(incumbent.feature_ids) <= set(candidate.feature_ids):
        raise ValueError("incumbent_features_removed")
    if incumbent and set(new_feature_ids) & set(incumbent.feature_ids):
        raise ValueError("candidate_feature_already_used")
    expected_features = set(new_feature_ids) | (set(incumbent.feature_ids) if incumbent else set())
    if set(candidate.feature_ids) != expected_features:
        raise ValueError("unregistered_candidate_features")
    if incumbent:
        if not incumbent.fit_rows_digest or not incumbent.fit_case_ids or not incumbent.fit_group_ids:
            raise ValueError("incumbent_training_provenance_missing")
        if heldout_cases & set(incumbent.fit_case_ids) or heldout_groups & set(incumbent.fit_group_ids):
            raise ValueError("incumbent_split_leakage")
    values = [candidate.predict(dict(row.features), candidate.evidence_contract_digest, candidate.backend) for row in heldout_rows]
    new_mae = mean(abs(value - finite(row.final_miou)) for value, row in zip(values, heldout_rows))
    benchmark = mean(row.final_miou for row in training_rows)
    old_values = [benchmark] * len(heldout_rows)
    if incumbent:
        old_values = [incumbent.score(dict(row.features), incumbent.evidence_contract_digest, incumbent.backend) for row in heldout_rows]
    old_mae = mean(abs(value - row.final_miou) for value, row in zip(old_values, heldout_rows))
    gain = None
    worst = None
    decisions = []
    if len(heldout_groups) < policy.minimum_heldout_groups:
        decisions.append("insufficient_coverage")
    if any(abs(candidate.weights[candidate.feature_ids.index(key)]) <= policy.minimum_weight for key in new_feature_ids):
        decisions.append("reject_unused_candidate_signal")
    changes = []
    for group in sorted(heldout_groups):
        cases = sorted({row.case_id for row in heldout_rows if row.group_id == group})
        group_changes = []
        for case in cases:
            indices = [i for i, row in enumerate(heldout_rows) if row.case_id == case]
            baselines = [i for i in indices if heldout_rows[i].is_baseline]
            if len(indices) < 2 or len(baselines) != 1:
                decisions.append("insufficient_selection_candidates")
                continue
            new_choice = max(indices, key=lambda i: (values[i], heldout_rows[i].is_baseline, heldout_rows[i].run_id))
            old_choice = max(indices, key=lambda i: (old_values[i], heldout_rows[i].is_baseline, heldout_rows[i].run_id)) if incumbent else baselines[0]
            group_changes.append(heldout_rows[new_choice].final_miou - heldout_rows[old_choice].final_miou)
        if group_changes:
            changes.append(mean(group_changes))
    if changes:
        gain, worst = mean(changes), min(changes)
    if new_mae > old_mae + policy.maximum_mae_drop or (gain is not None and gain < policy.minimum_selection_gain) or (worst is not None and worst < -policy.maximum_group_drop):
        decisions.append("reject_validation_regression")
    decision = decisions[0] if decisions else "accept"
    return ProxyValidation(decision, old_mae, new_mae, gain, worst, tuple(sorted(heldout_groups)),
                           digest(candidate), digest({"training": training_rows, "heldout": heldout_rows}), digest(policy),
                           digest(incumbent) if incumbent else None)


def release_proxy(candidate: FrozenProxy, validation: ProxyValidation) -> FrozenProxy:
    if validation.decision != "accept" or validation.candidate_proxy_digest != digest(candidate):
        raise ValueError("proxy_release_not_validated")
    return replace(candidate, validation_receipt=digest(validation))
