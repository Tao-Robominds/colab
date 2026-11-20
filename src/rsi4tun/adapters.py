from dataclasses import asdict
from math import cos, floor, isfinite, pi, sin
from pathlib import Path
from statistics import median

from rsi4tun.contracts import CompletedRun, FULL_STAGES, digest, file_digest, save_once
from rsi4tun.evidence import ArtifactBundle, BoundaryArtifact, DepthArtifact, KArtifact


def _configuration(configuration):
    allowed = {"missing_columns", "phase_correction_turns", "depth_k_coupling"}
    if set(configuration) - allowed:
        raise ValueError("unsupported_synthetic_configuration")
    missing = configuration.get("missing_columns", 3)
    correction = configuration.get("phase_correction_turns", 0.0)
    coupling = configuration.get("depth_k_coupling", 0.4)
    if type(missing) is not int or not 0 <= missing < 12:
        raise ValueError("invalid_missing_columns")
    for value in (correction, coupling):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not isfinite(value):
            raise ValueError("invalid_synthetic_parameter")
    if not -0.4 <= correction <= 0.4 or not 0 <= coupling <= 1:
        raise ValueError("synthetic_parameter_out_of_range")
    phase = 0.1 + coupling * missing / 12 - correction
    if not -0.49 < phase < 0.49:
        raise ValueError("synthetic_phase_out_of_domain")
    return missing, float(correction), float(coupling), phase


def run_synthetic(case: dict, configuration: dict, output_dir: Path, code_commit: str, code_tree: str) -> CompletedRun:
    if set(case) - {"case_id", "scan_id", "backend", "design_schema"}:
        raise ValueError("unsupported_synthetic_case_field")
    if not isinstance(case.get("case_id"), str) or not case["case_id"]:
        raise ValueError("missing_case_identity")
    if any(not isinstance(value, str) or not value for value in case.values()):
        raise ValueError("invalid_synthetic_case_identity")
    if case.get("backend", "synthetic") != "synthetic":
        raise ValueError("synthetic_backend_required")
    if not isinstance(code_commit, str) or not code_commit or not isinstance(code_tree, str) or not code_tree:
        raise ValueError("missing_executed_code_revision")
    missing, correction, coupling, phase = _configuration(configuration)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stage_directory = output / "stages"
    stage_directory.mkdir(exist_ok=False)
    input_digest = digest(case)
    config_digest = digest({"missing_columns": missing, "phase_correction_turns": correction, "depth_k_coupling": coupling})
    run_id = "synthetic-" + digest((input_digest, config_digest, code_commit, code_tree))[:20]
    stage_digests = []

    def emit(stage, payload):
        target = stage_directory / (stage + ".json")
        save_once(target, {
            "stage": stage,
            "backend": "synthetic",
            "code_commit": code_commit,
            "input_digest": input_digest,
            "configuration_digest": config_digest,
            "input_stage_digest": stage_digests[-1][1] if stage_digests else None,
            "data": payload,
        })
        checksum = file_digest(target)
        stage_digests.append((stage, checksum))
        return checksum

    rows, columns = 3, 12
    raw_depth = tuple(tuple(5.0 + 0.05 * row + 0.01 * (column % 3) - (0.1 if column % 3 == 0 else 0.0) for column in range(columns)) for row in range(rows))
    valid = tuple(tuple(column >= missing for column in range(columns)) for _ in range(rows))
    expected = tuple(tuple(True for _ in range(columns)) for _ in range(rows))
    unfolded = tuple(tuple(raw_depth[row][column] if valid[row][column] else None for column in range(columns)) for row in range(rows))
    intensity = tuple(tuple(1.0 if column % 3 == 0 else 0.0 for column in range(columns)) for _ in range(rows))
    emit("unfolding", {"depth_values": unfolded, "valid": valid, "expected_support": expected, "intensity": intensity, "grid_pitch_m": (1.0, 1.0)})

    denoised = tuple(tuple(median(unfolded[row][neighbour % columns] for neighbour in (column - 1, column, column + 1) if unfolded[row][neighbour % columns] is not None) if valid[row][column] else None for column in range(columns)) for row in range(rows))
    depth = DepthArtifact(denoised, valid, expected, 1.0, 1.0, True)
    depth_digest = emit("denoising", asdict(depth))

    finite_values = [value for row in denoised for value in row if value is not None]
    low, high = min(finite_values), max(finite_values)
    enhanced = tuple(tuple((value - low) / (high - low) if value is not None and high > low else (0.0 if value is not None else None) for value in row) for row in denoised)
    emit("enhancement", {"normalised_depth": enhanced, "intensity": intensity, "normalisation_range_m": (low, high)})

    support = tuple(tuple(column / columns for column, value in enumerate(ring) if value > 0.5) for ring in intensity)
    measured_coverage = sum(value for ring in depth.valid for value in ring) / (rows * columns)
    phase = 0.1 + coupling * (1.0 - measured_coverage) - correction
    detected = tuple(tuple((position + phase / 4) % 1.0 for position in ring) for ring in support)
    boundaries = BoundaryArtifact(detected, support, 12.0, "synthetic_geometry_detector_v1", "synthetic_intensity_edges_v1")
    k = KArtifact(tuple((0.125 + phase) % 1.0 for _ in range(rows)), tuple(0.125 for _ in range(rows)), tuple(0.0 for _ in range(rows)), 1.0, True)
    geometry_digest = emit("joint_and_k_localisation", {"boundaries": asdict(boundaries), "k": asdict(k)})

    prompts = tuple(tuple(((position + 0.125) % 1.0, row + 0.5) for position in ring) for row, ring in enumerate(detected))
    k_prompts = tuple((azimuth, row + 0.5) for row, azimuth in enumerate(k.azimuth_turns))
    emit("prompt_generation", {"positive_points_turns_pitch": prompts, "k_positive_points_turns_pitch": k_prompts})

    point_ids = tuple(range(rows * columns))
    prompt_phases = tuple((azimuth - 0.125 + 0.5) % 1.0 - 0.5 for azimuth, _ in k_prompts)
    instances = tuple(int(floor(((point_id % columns) / columns - prompt_phases[point_id // columns]) % 1.0 * 4)) for point_id in point_ids)
    masks = tuple(tuple(point_id for point_id, instance in zip(point_ids, instances) if instance == mask_id) for mask_id in range(4))
    emit("sam_segmentation", {"backend": "synthetic_partition", "instance_ids": instances, "instance_masks": masks})

    identity_map = ((0, 0), (1, 1), (2, 2), (3, 3))
    predictions = tuple(dict(identity_map)[instance] for instance in instances)
    emit("semantic_assignment", {"semantic_identity_map": identity_map, "point_ids": point_ids, "predicted_labels": predictions})

    coordinates = tuple((raw_depth[point_id // columns][point_id % columns] * cos(2 * pi * (point_id % columns) / columns), raw_depth[point_id // columns][point_id % columns] * sin(2 * pi * (point_id % columns) / columns), float(point_id // columns)) for point_id in point_ids)
    final_digest = emit("reprojection_3d", {"point_ids": point_ids, "coordinates_m": coordinates, "predicted_labels": predictions})

    bundle = ArtifactBundle(
        bundle_id=run_id + "-artifacts",
        case_id=case["case_id"],
        backend="synthetic",
        code_commit=code_commit,
        artifact_digests=(("depth", depth_digest), ("boundaries", geometry_digest), ("k", geometry_digest), ("final_3d", final_digest)),
        completed_stages=FULL_STAGES,
        design_schema=case.get("design_schema", "synthetic_design"),
        expected_boundaries_per_ring=4,
        representation_id="synthetic_unwrap_turns_pitch_v1",
        registration_id="synthetic_registered_geometry_v1",
        registration_audited=True,
        depth=depth,
        boundaries=boundaries,
        k=k,
    )
    artifact_path = output / "artifacts.json"
    save_once(artifact_path, bundle)
    run = CompletedRun(
        run_id=run_id,
        case_id=case["case_id"],
        input_digest=input_digest,
        code_commit=code_commit,
        code_tree=code_tree,
        backend="synthetic",
        stage_trace=FULL_STAGES,
        stage_digests=tuple(stage_digests),
        point_ids=point_ids,
        predicted_labels=predictions,
        artifact_path=str(artifact_path),
        artifact_sha256=file_digest(artifact_path),
    )
    run.require_complete()
    save_once(output / "run.json", run)
    return run


class SAM4TunAdapter:
    def run(self, case: dict, configuration: dict, output_dir: Path, code_commit: str, code_tree: str) -> CompletedRun:
        raise NotImplementedError("real_sam4tun_integration_not_configured")
