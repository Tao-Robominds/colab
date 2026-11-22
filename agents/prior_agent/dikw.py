from __future__ import annotations

import json
from pathlib import Path


def append_section(path: Path, heading: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    block = f"## {heading}\n\n{body.rstrip()}\n"
    if path.is_file():
        existing = path.read_text().rstrip() + "\n\n"
        path.write_text(existing + block)
    else:
        title = path.stem.replace("_", " ")
        path.write_text(f"# {title}\n\n{block}")


def record_arm(
    dikw_root: Path,
    arm_name: str,
    action: dict,
    metrics: dict,
    spill: int,
    guard_ok: bool,
    guard_fails: list[str],
    prediction_held: bool,
) -> None:
    data_body = (
        f"Arm `{arm_name}` scored mean IoU {metrics['mIoU']:.3f}. "
        f"Spill was {spill}. "
        + " ".join(f"{name} IoU was {value:.3f}." for name, value in metrics["classes"].items())
    )
    append_section(dikw_root / "data" / "1_1_tune.md", arm_name, data_body)

    held = action.get("overrides") or {}
    info_body = (
        f"Action was `{action.get('action')}`. "
        f"Predicted mean IoU was {action.get('predicted_miou')}. "
        f"Overrides were `{json.dumps(held, sort_keys=True)}`."
    )
    if action.get("source_arm"):
        info_body += f" Source arm was `{action['source_arm']}`."
    append_section(dikw_root / "information" / "1_1_tune.md", arm_name, info_body)

    knowledge_body = (
        f"The sealed prediction held: {prediction_held}. "
        f"Lining guard passed: {guard_ok}."
        + (f" Guard failures: {'; '.join(guard_fails)}." if guard_fails else "")
    )
    append_section(
        dikw_root / "information" / "research_notes" / "1_1_tune.md",
        arm_name,
        knowledge_body,
    )


def sample_proxy_prediction(sample_proxy: dict, features: dict) -> float:
    intercept = float(sample_proxy["intercept"])
    total = intercept
    for key, centre, scale, weight in zip(
        sample_proxy["feature_ids"],
        sample_proxy["centres"],
        sample_proxy["scales"],
        sample_proxy["weights"],
    ):
        total += float(weight) * (float(features[key]) - float(centre)) / float(scale)
    return max(0.0, min(1.0, total))


def features_from_action(action: dict, base_features: dict) -> dict:
    feats = dict(base_features)
    overrides = action.get("overrides") or {}
    sam = overrides.get("parameters_sam.json") or {}
    if "mirror_k_geometry" in sam:
        feats["k_wedge"] = 1.0 if sam["mirror_k_geometry"] else 0.0
    if "angle" in sam:
        feats["angle_positive"] = 1.0 if float(sam["angle"]) > 0 else 0.0
    if "AB_height" in sam:
        ab = float(sam["AB_height"])
        feats["ab_rel_error"] = abs(ab - 3239.77) / 3239.77
    if action.get("action") == "proud_replay":
        feats["proud_cut"] = 1.0
    if float(sam.get("proud_residual_mm", 0) or 0) > 0:
        feats["proud_cut"] = 1.0
    return feats


def maybe_refit_seam_proxy(
    wisdom_dir: Path,
    rows: list[dict],
    *,
    border_area_ratio: float,
    baseline_miou: float,
    latest_miou: float,
    tolerance: float = 0.01,
    border_filled: float = 0.8,
) -> Path | None:
    if border_area_ratio < border_filled:
        return None
    if abs(latest_miou - baseline_miou) <= tolerance:
        return None
    from rsi4tun.proxy import DevelopmentRow, fit_proxy

    feature_ids = ("k_wedge", "angle_positive", "ab_rel_error", "proud_cut", "border_area_ratio")
    development = tuple(
        DevelopmentRow(
            "1-1",
            "1-1",
            row["run_id"],
            tuple((key, float(row["features"][key])) for key in feature_ids),
            float(row["miou"]),
            bool(row.get("is_baseline", False)),
        )
        for row in rows
        if all(key in row["features"] for key in feature_ids)
    )
    if len(development) < 2:
        return None
    fitted = fit_proxy(
        development,
        feature_ids,
        proxy_id="1_1_tune_seam_v1",
        evidence_contract_digest="1-1-tune-proxy-seam-v1",
        backend="1_1_tune",
    )
    record = {
        "proxy_id": fitted.proxy_id,
        "target": "final_3d_semantic_miou",
        "status": "development_fit_pending",
        "scope": {
            "family": "staggered",
            "scan": "data/scans/1-1.txt",
            "case_id": "1-1",
            "group_id": "1-1",
        },
        "feature_ids": list(fitted.feature_ids),
        "centres": list(fitted.centres),
        "scales": list(fitted.scales),
        "weights": list(fitted.weights),
        "intercept": fitted.intercept,
        "evidence_contract_digest": fitted.evidence_contract_digest,
        "backend": fitted.backend,
        "validation_receipt": fitted.validation_receipt,
        "fit_rows_digest": fitted.fit_rows_digest,
        "n_rows": len(development),
        "equation": "clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)",
        "notes": (
            "Development fit including border_area_ratio. One group. "
            "Not accepted wisdom. Not a released proxy."
        ),
    }
    out = wisdom_dir / "1_1_proxy_seam.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    return out


def record_seam_outcome(
    dikw_root: Path,
    arm_name: str,
    *,
    sealed: dict,
    vector: dict,
    miou: float,
    rule: str,
) -> None:
    body = (
        f"Arm `{arm_name}` sealed border ratio {sealed.get('predicted_border_area_ratio')}. "
        f"Observed border ratio {vector.get('border_area_ratio')}. "
        f"Mean IoU {miou:.3f}. Rule `{rule}`."
    )
    append_section(
        dikw_root / "information" / "research_notes" / "1_1_seam_diagnosis.md",
        arm_name,
        body,
    )


def maybe_refit_1_1_proxy(
    wisdom_dir: Path,
    sample_proxy_path: Path,
    rows: list[dict],
    latest_features: dict,
    latest_miou: float,
) -> Path | None:
    out = wisdom_dir / "1_1_proxy.json"
    if out.is_file():
        current = json.loads(out.read_text())
        if int(current.get("n_rows") or 0) > len(rows):
            return None
    sample = json.loads(sample_proxy_path.read_text())
    predicted = sample_proxy_prediction(sample, latest_features)
    if abs(predicted - latest_miou) <= 0.02 and len(rows) < 3:
        return None
    from rsi4tun.proxy import DevelopmentRow, fit_proxy

    feature_ids = tuple(sample["feature_ids"])
    development = tuple(
        DevelopmentRow(
            "1-1",
            "1-1",
            row["run_id"],
            tuple((key, float(row["features"][key])) for key in feature_ids),
            float(row["miou"]),
            bool(row.get("is_baseline", False)),
        )
        for row in rows
    )
    fitted = fit_proxy(
        development,
        feature_ids,
        proxy_id="1_1_tune_v1",
        evidence_contract_digest="1-1-tune-proxy-v1",
        backend="1_1_tune",
    )
    record = {
        "proxy_id": fitted.proxy_id,
        "target": "final_3d_semantic_miou",
        "status": "development_fit_pending",
        "scope": {
            "family": "staggered",
            "scan": "data/scans/1-1.txt",
            "case_id": "1-1",
            "group_id": "1-1",
        },
        "feature_ids": list(fitted.feature_ids),
        "centres": list(fitted.centres),
        "scales": list(fitted.scales),
        "weights": list(fitted.weights),
        "intercept": fitted.intercept,
        "evidence_contract_digest": fitted.evidence_contract_digest,
        "backend": fitted.backend,
        "validation_receipt": fitted.validation_receipt,
        "fit_rows_digest": fitted.fit_rows_digest,
        "n_rows": len(development),
        "equation": "clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)",
        "notes": "Development fit on scan 1-1. Not accepted wisdom.",
    }
    out.write_text(json.dumps(record, indent=2) + "\n")
    return out
