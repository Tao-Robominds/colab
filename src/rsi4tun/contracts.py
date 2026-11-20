from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any


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
OBJECTIVE = "final_3d_semantic_miou"
PROTOCOL = "executable-evidence-v1"


def canonical(value: Any) -> bytes:
    def convert(item):
        if is_dataclass(item):
            return asdict(item)
        if isinstance(item, Path):
            return str(item)
        raise TypeError(type(item).__name__)
    return json.dumps(value, default=convert, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def save_once(path: Path, value: Any) -> str:
    data = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.write(b"\n")
    return sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    with path.open() as stream:
        return json.load(stream)


def finite(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("non_finite_measurement")
    return float(value)


@dataclass(frozen=True)
class CompletedRun:
    run_id: str
    case_id: str
    input_digest: str
    code_commit: str
    code_tree: str
    backend: str
    stage_trace: tuple[str, ...]
    stage_digests: tuple[tuple[str, str], ...]
    point_ids: tuple[int, ...]
    predicted_labels: tuple[int, ...]
    artifact_path: str
    artifact_sha256: str

    def require_complete(self) -> None:
        if self.stage_trace != FULL_STAGES:
            raise ValueError("incomplete_pipeline")
        if tuple(name for name, _ in self.stage_digests) != FULL_STAGES:
            raise ValueError("incomplete_stage_artifacts")
        if any(not isinstance(value, str) or not value for value in (
            self.run_id, self.case_id, self.backend, self.code_commit, self.code_tree, self.input_digest
        )):
            raise ValueError("missing_run_provenance")
        if not self.point_ids or any(type(value) is not int for value in self.point_ids) or len(self.point_ids) != len(set(self.point_ids)):
            raise ValueError("invalid_point_identity")
        if len(self.point_ids) != len(self.predicted_labels) or any(type(value) is not int for value in self.predicted_labels):
            raise ValueError("incomplete_final_labels")
        artifact_path = Path(self.artifact_path)
        if artifact_path.is_symlink() or not artifact_path.is_file() or file_digest(artifact_path) != self.artifact_sha256:
            raise ValueError("artifact_integrity_failure")
        bundle = read_json(artifact_path)
        if not isinstance(bundle, dict):
            raise ValueError("invalid_artifact_bundle")
        if (bundle.get("case_id"), bundle.get("code_commit"), bundle.get("backend")) != (self.case_id, self.code_commit, self.backend):
            raise ValueError("artifact_run_provenance_mismatch")
        if tuple(bundle.get("completed_stages", ())) != FULL_STAGES:
            raise ValueError("artifact_pipeline_mismatch")
        for _, value in self.stage_digests:
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError("invalid_stage_digest")
        stages = {}
        previous_digest = None
        configuration_digest = None
        for name, value in self.stage_digests:
            stage_path = artifact_path.parent / "stages" / (name + ".json")
            if stage_path.is_symlink() or not stage_path.is_file() or file_digest(stage_path) != value:
                raise ValueError("stage_integrity_failure")
            stage = read_json(stage_path)
            if not isinstance(stage, dict) or not isinstance(stage.get("data"), dict):
                raise ValueError("invalid_stage_payload")
            if (stage.get("stage"), stage.get("code_commit"), stage.get("input_digest"), stage.get("backend")) != (
                name, self.code_commit, self.input_digest, self.backend
            ):
                raise ValueError("stage_run_provenance_mismatch")
            if stage.get("code_tree", self.code_tree) != self.code_tree:
                raise ValueError("stage_run_provenance_mismatch")
            if stage.get("input_stage_digest") != previous_digest:
                raise ValueError("stage_chain_mismatch")
            stage_configuration = stage.get("configuration_digest")
            if not isinstance(stage_configuration, str) or len(stage_configuration) != 64 or any(char not in "0123456789abcdef" for char in stage_configuration):
                raise ValueError("invalid_configuration_digest")
            if configuration_digest is not None and stage_configuration != configuration_digest:
                raise ValueError("stage_configuration_mismatch")
            configuration_digest = stage_configuration
            previous_digest = value
            stages[name] = stage["data"]
        final = stages["reprojection_3d"]
        if tuple(final.get("point_ids", ())) != self.point_ids or tuple(final.get("predicted_labels", ())) != self.predicted_labels:
            raise ValueError("final_labels_stage_mismatch")
        named_pairs = bundle.get("artifact_digests", ())
        if any(not isinstance(pair, (list, tuple)) or len(pair) != 2 for pair in named_pairs):
            raise ValueError("invalid_named_artifact_digests")
        named = dict(named_pairs)
        if len(named) != len(named_pairs):
            raise ValueError("duplicate_named_artifact_digest")
        hashes = dict(self.stage_digests)
        expected = {
            "depth": hashes["denoising"],
            "boundaries": hashes["joint_and_k_localisation"],
            "k": hashes["joint_and_k_localisation"],
            "final_3d": hashes["reprojection_3d"],
        }
        if any(named.get(name) != value for name, value in expected.items()):
            raise ValueError("named_artifact_stage_mismatch")
        geometry = stages["joint_and_k_localisation"]
        if any(not isinstance(bundle.get(name), dict) for name in ("depth", "boundaries", "k")) or any(not isinstance(geometry.get(name), dict) for name in ("boundaries", "k")):
            raise ValueError("missing_stage_evidence")
        if digest(bundle.get("depth")) != digest(stages["denoising"]):
            raise ValueError("depth_stage_data_mismatch")
        if digest(bundle.get("boundaries")) != digest(geometry.get("boundaries")):
            raise ValueError("boundary_stage_data_mismatch")
        if digest(bundle.get("k")) != digest(geometry.get("k")):
            raise ValueError("k_stage_data_mismatch")


def run_from_dict(value: dict) -> CompletedRun:
    data = dict(value)
    for name in ("stage_trace", "point_ids", "predicted_labels"):
        data[name] = tuple(data[name])
    data["stage_digests"] = tuple(tuple(pair) for pair in data["stage_digests"])
    return CompletedRun(**data)
