from dataclasses import asdict, dataclass
from hashlib import sha256
from json import dumps
from math import atan2, cos, isfinite, pi, sin, sqrt


FULL_STAGES = (
    "unfolding",
    "denoising",
    "enhancement",
    "joint_and_k_localisation",
    "prompt_generation",
    "sam_segmentation",
    "semantic_assignment",
    "reprojection_3d",
)


@dataclass(frozen=True)
class DepthArtifact:
    values: tuple[tuple[float | None, ...], ...]
    valid: tuple[tuple[bool, ...], ...]
    expected_support: tuple[tuple[bool, ...], ...]
    row_pitch_m: float
    column_pitch_m: float
    periodic_columns: bool = True


@dataclass(frozen=True)
class BoundaryArtifact:
    detected_turns: tuple[tuple[float, ...], ...]
    support_turns: tuple[tuple[float, ...], ...]
    circumference_m: float
    detector_id: str
    support_extractor_id: str


@dataclass(frozen=True)
class KArtifact:
    azimuth_turns: tuple[float, ...]
    expected_azimuth_turns: tuple[float, ...]
    axial_offsets_m: tuple[float, ...]
    ring_pitch_m: float
    identity_known: bool


@dataclass(frozen=True)
class ArtifactBundle:
    bundle_id: str
    case_id: str
    backend: str
    code_commit: str
    artifact_digests: tuple[tuple[str, str], ...]
    completed_stages: tuple[str, ...]
    design_schema: str
    expected_boundaries_per_ring: int | None
    representation_id: str
    registration_id: str
    registration_audited: bool
    depth: DepthArtifact
    boundaries: BoundaryArtifact
    k: KArtifact
    source_role: str = "experiment"
    expert_review_id: str | None = None


@dataclass(frozen=True)
class ComparisonPolicy:
    boundary_tolerance_m: float
    supported_designs: tuple[str, ...]
    expected_stages: tuple[str, ...] = FULL_STAGES
    version: str = "comparison-v1"


@dataclass(frozen=True)
class ComparisonReport:
    status: str
    measurements: dict[str, float]
    reference_measurements: dict[str, float]
    deviations: dict[str, float]
    features: dict[str, float]
    reasons: tuple[str, ...]
    provenance: dict[str, object]


def bundle_from_dict(value):
    payload = dict(value)
    depth = dict(payload["depth"])
    for key in ("values", "valid", "expected_support"):
        depth[key] = tuple(tuple(row) for row in depth[key])
    payload["depth"] = DepthArtifact(**depth)
    boundaries = dict(payload["boundaries"])
    for key in ("detected_turns", "support_turns"):
        boundaries[key] = tuple(tuple(row) for row in boundaries[key])
    payload["boundaries"] = BoundaryArtifact(**boundaries)
    k = dict(payload["k"])
    for key in ("azimuth_turns", "expected_azimuth_turns", "axial_offsets_m"):
        k[key] = tuple(k[key])
    payload["k"] = KArtifact(**k)
    payload["artifact_digests"] = tuple(tuple(item) for item in payload["artifact_digests"])
    payload["completed_stages"] = tuple(payload["completed_stages"])
    return ArtifactBundle(**payload)


def policy_from_dict(value):
    payload = dict(value)
    payload["supported_designs"] = tuple(payload["supported_designs"])
    if "expected_stages" in payload:
        payload["expected_stages"] = tuple(payload["expected_stages"])
    return ComparisonPolicy(**payload)


def assert_fixed_evidence(baseline, arm):
    for key in ("case_id", "backend", "design_schema", "expected_boundaries_per_ring", "representation_id", "registration_id", "registration_audited"):
        if getattr(baseline, key) != getattr(arm, key):
            raise ValueError("evidence_contract_changed:" + key)
    for key in ("expected_support", "row_pitch_m", "column_pitch_m", "periodic_columns"):
        if getattr(baseline.depth, key) != getattr(arm.depth, key):
            raise ValueError("evidence_contract_changed:depth." + key)
    if tuple(len(row) for row in baseline.depth.values) != tuple(len(row) for row in arm.depth.values):
        raise ValueError("evidence_contract_changed:depth.shape")
    for key in ("support_turns", "circumference_m", "support_extractor_id"):
        if getattr(baseline.boundaries, key) != getattr(arm.boundaries, key):
            raise ValueError("evidence_contract_changed:boundaries." + key)
    for key in ("expected_azimuth_turns", "ring_pitch_m", "identity_known"):
        if getattr(baseline.k, key) != getattr(arm.k, key):
            raise ValueError("evidence_contract_changed:k." + key)


def _digest(value):
    return sha256(dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and isfinite(value)


def _positive(value):
    return _number(value) and value > 0


def _turn_distance(first, second):
    return abs((first - second + 0.5) % 1.0 - 0.5)


def _validate_depth(depth):
    if not depth.values or not depth.values[0]:
        raise ValueError("empty_depth")
    rows, columns = len(depth.values), len(depth.values[0])
    if not _positive(depth.row_pitch_m) or not _positive(depth.column_pitch_m):
        raise ValueError("invalid_grid_pitch")
    if type(depth.periodic_columns) is not bool:
        raise ValueError("invalid_periodic_flag")
    if any(len(matrix) != rows or any(len(row) != columns for row in matrix) for matrix in (depth.values, depth.valid, depth.expected_support)):
        raise ValueError("depth_shape_mismatch")
    for row in range(rows):
        for column in range(columns):
            value = depth.values[row][column]
            if type(depth.valid[row][column]) is not bool or type(depth.expected_support[row][column]) is not bool:
                raise ValueError("invalid_depth_mask")
            if value is not None and not _number(value):
                raise ValueError("nonfinite_depth")
            if depth.valid[row][column] and value is None:
                raise ValueError("missing_valid_depth")
    if not any(value for row in depth.expected_support for value in row):
        raise ValueError("empty_expected_support")


def _depth_measurements(depth):
    _validate_depth(depth)
    rows, columns = len(depth.values), len(depth.values[0])
    expected = {(row, column) for row in range(rows) for column in range(columns) if depth.expected_support[row][column]}
    holes = {(row, column) for row, column in expected if not depth.valid[row][column]}
    remaining, largest = set(holes), 0
    while remaining:
        frontier, size = [remaining.pop()], 0
        while frontier:
            row, column = frontier.pop()
            size += 1
            neighbours = [(row - 1, column), (row + 1, column)]
            for next_column in (column - 1, column + 1):
                if depth.periodic_columns:
                    neighbours.append((row, next_column % columns))
                elif 0 <= next_column < columns:
                    neighbours.append((row, next_column))
            for neighbour in neighbours:
                if neighbour in remaining:
                    remaining.remove(neighbour)
                    frontier.append(neighbour)
        largest = max(largest, size)
    return {
        "depth_valid_coverage": (len(expected) - len(holes)) / len(expected),
        "depth_largest_hole_fraction": largest / len(expected),
        "depth_expected_area_m2": len(expected) * depth.row_pitch_m * depth.column_pitch_m,
    }


def _boundary_measurements(boundaries, expected_count, tolerance):
    if not _positive(boundaries.circumference_m):
        raise ValueError("invalid_circumference")
    if not boundaries.detector_id or not boundaries.support_extractor_id:
        raise ValueError("missing_edge_provenance")
    if boundaries.detector_id == boundaries.support_extractor_id:
        raise ValueError("self_referential_boundary_support")
    if not boundaries.detected_turns or len(boundaries.detected_turns) != len(boundaries.support_turns):
        raise ValueError("boundary_ring_mismatch")
    distances_detected, distances_support = [], []
    for detected, support in zip(boundaries.detected_turns, boundaries.support_turns):
        if not detected or not support:
            raise ValueError("empty_boundary_evidence")
        for positions in (detected, support):
            if any(not _number(value) or not 0 <= value < 1 for value in positions):
                raise ValueError("invalid_boundary_position")
            if len(set(positions)) != len(positions):
                raise ValueError("duplicate_boundary_position")
        distances_detected.extend(min(_turn_distance(value, target) for target in support) for value in detected)
        distances_support.extend(min(_turn_distance(value, target) for target in detected) for value in support)
    turn_tolerance = tolerance / boundaries.circumference_m
    result = {
        "boundary_support_precision": sum(value <= turn_tolerance for value in distances_detected) / len(distances_detected),
        "boundary_support_recall": sum(value <= turn_tolerance for value in distances_support) / len(distances_support),
        "boundary_symmetric_distance_fraction": 0.5 * (sum(distances_detected) / len(distances_detected) + sum(distances_support) / len(distances_support)),
    }
    if expected_count is not None:
        if type(expected_count) is not int or expected_count <= 0:
            raise ValueError("invalid_expected_boundary_count")
        result["boundary_count_error_fraction"] = sum(abs(len(ring) - expected_count) / expected_count for ring in boundaries.detected_turns) / len(boundaries.detected_turns)
    return result


def _k_measurements(k, ring_count):
    if type(k.identity_known) is not bool:
        raise ValueError("invalid_k_identity_flag")
    if not _positive(k.ring_pitch_m):
        raise ValueError("invalid_ring_pitch")
    if not k.identity_known:
        return {}, ("k_identity_unknown",)
    if ring_count <= 0:
        raise ValueError("empty_k_evidence")
    if any(len(values) != ring_count for values in (k.azimuth_turns, k.expected_azimuth_turns, k.axial_offsets_m)):
        raise ValueError("k_ring_mismatch")
    if any(not _number(value) or not 0 <= value < 1 for values in (k.azimuth_turns, k.expected_azimuth_turns) for value in values):
        raise ValueError("invalid_k_azimuth")
    if any(not _number(value) for value in k.axial_offsets_m):
        raise ValueError("invalid_k_axial_offset")
    residuals = [(observed - expected + 0.5) % 1.0 - 0.5 for observed, expected in zip(k.azimuth_turns, k.expected_azimuth_turns)]
    mean_cos = sum(cos(2 * pi * value) for value in residuals) / ring_count
    mean_sin = sum(sin(2 * pi * value) for value in residuals) / ring_count
    result = {
        "k_phase_rms_turns": sqrt(sum(value * value for value in residuals) / ring_count),
        "k_axial_rms_pitch": sqrt(sum((value / k.ring_pitch_m) ** 2 for value in k.axial_offsets_m) / ring_count),
    }
    if sqrt(mean_cos * mean_cos + mean_sin * mean_sin) < 1e-9:
        return result, ("k_phase_mean_undefined",)
    mean_turn = atan2(mean_sin, mean_cos) / (2 * pi)
    result["k_phase_spread_turns"] = sqrt(sum(_turn_distance(value, mean_turn) ** 2 for value in residuals) / ring_count)
    return result, ()


def _validate_bundle(bundle, policy):
    if not _positive(policy.boundary_tolerance_m):
        raise ValueError("invalid_comparison_policy")
    if bundle.completed_stages != policy.expected_stages or policy.expected_stages != FULL_STAGES:
        raise ValueError("incomplete_full_pipeline")
    if not bundle.bundle_id or not bundle.case_id or not bundle.code_commit or not bundle.backend:
        raise ValueError("missing_bundle_provenance")
    if len(dict(bundle.artifact_digests)) != len(bundle.artifact_digests):
        raise ValueError("duplicate_artifact_digest")
    if not {"depth", "boundaries", "k", "final_3d"}.issubset(dict(bundle.artifact_digests)) or not all(key and value for key, value in bundle.artifact_digests):
        raise ValueError("missing_artifact_digest")


def measure_artifacts(bundle, policy):
    _validate_bundle(bundle, policy)
    result = _depth_measurements(bundle.depth)
    result.update(_boundary_measurements(bundle.boundaries, bundle.expected_boundaries_per_ring, policy.boundary_tolerance_m))
    k_values, reasons = _k_measurements(bundle.k, len(bundle.boundaries.detected_turns))
    result.update(k_values)
    return result, reasons


def diagnostic_measurements(bundle, policy):
    try:
        _validate_bundle(bundle, policy)
    except (ValueError, TypeError, OverflowError) as error:
        return {}, {"pipeline": "invalid:" + str(error)}
    measurements, statuses = {}, {}
    evaluators = (
        ("depth", lambda: (_depth_measurements(bundle.depth), ())),
        ("boundaries", lambda: (_boundary_measurements(bundle.boundaries, bundle.expected_boundaries_per_ring, policy.boundary_tolerance_m), ())),
        ("k", lambda: _k_measurements(bundle.k, len(bundle.boundaries.detected_turns))),
    )
    for component, evaluate in evaluators:
        try:
            values, reasons = evaluate()
            measurements.update(values)
            statuses[component] = "partial:" + ",".join(reasons) if reasons else "valid"
        except (ValueError, TypeError, OverflowError) as error:
            statuses[component] = "invalid:" + str(error)
    return measurements, statuses


def compare_reference(reference, observed, policy):
    provenance = {
        "reference_id": reference.bundle_id,
        "observed_id": observed.bundle_id,
        "reference_case": reference.case_id,
        "observed_case": observed.case_id,
        "reference_commit": reference.code_commit,
        "observed_commit": observed.code_commit,
        "reference_artifact_digests": dict(reference.artifact_digests),
        "observed_artifact_digests": dict(observed.artifact_digests),
        "reference_registration": reference.registration_id,
        "observed_registration": observed.registration_id,
        "policy_version": policy.version,
        "reference_role": reference.source_role,
        "reference_expert_review": reference.expert_review_id,
    }
    if not _positive(policy.boundary_tolerance_m) or not policy.version:
        return ComparisonReport("invalid", {}, {}, {}, {}, ("invalid_comparison_policy",), provenance)
    try:
        provenance["policy_digest"] = _digest(asdict(policy))
        reference_measurements, reference_reasons = measure_artifacts(reference, policy)
        measurements, observed_reasons = measure_artifacts(observed, policy)
        provenance["reference_bundle_digest"] = _digest(asdict(reference))
        provenance["observed_bundle_digest"] = _digest(asdict(observed))
    except (ValueError, TypeError, OverflowError) as error:
        reference_measurements, reference_statuses = diagnostic_measurements(reference, policy)
        measurements, observed_statuses = diagnostic_measurements(observed, policy)
        provenance["component_status"] = {"reference": reference_statuses, "observed": observed_statuses}
        return ComparisonReport("invalid", measurements, reference_measurements, {}, {}, (str(error),), provenance)
    if reference.source_role != "expert_reference" or not reference.expert_review_id:
        return ComparisonReport("insufficient_reference", measurements, reference_measurements, {}, {}, ("expert_reference_not_reviewed",), provenance)
    coverage_reasons = []
    if not reference.design_schema or not observed.design_schema or reference.design_schema != observed.design_schema or observed.design_schema not in policy.supported_designs:
        coverage_reasons.append("design_coverage_gap")
    if reference.expected_boundaries_per_ring is None or observed.expected_boundaries_per_ring is None or reference.expected_boundaries_per_ring != observed.expected_boundaries_per_ring:
        coverage_reasons.append("design_boundary_count_unmatched")
    if not reference.representation_id or reference.representation_id != observed.representation_id:
        coverage_reasons.append("representation_unmatched")
    if not reference.registration_id or not observed.registration_id or reference.registration_audited is not True or observed.registration_audited is not True:
        coverage_reasons.append("registration_not_audited")
    if reference.backend != observed.backend:
        coverage_reasons.append("backend_unmatched")
    if coverage_reasons:
        return ComparisonReport("coverage_gap", measurements, reference_measurements, {}, {}, tuple(coverage_reasons), provenance)
    reasons = tuple(dict.fromkeys(reference_reasons + observed_reasons))
    keys = sorted(set(measurements) & set(reference_measurements) - {"depth_expected_area_m2"})
    deviations = {key: measurements[key] - reference_measurements[key] for key in keys}
    features = {key + "__delta": value for key, value in deviations.items()}
    return ComparisonReport("partial" if reasons else "comparable", measurements, reference_measurements, deviations, features, reasons, provenance)
