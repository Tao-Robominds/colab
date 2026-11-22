import json
from pathlib import Path
from statistics import mean

from rsi4tun.proxy import DevelopmentRow, FrozenProxy, fit_proxy

FEATURE_IDS = (
    "proud_mm",
    "mid_mask",
    "ring2_shift",
    "theta_split",
    "dark_m1400",
    "wrap_theta",
    "ab_rel_error",
    "scale_dev",
    "walk_swapped",
    "mask_off",
    "a1_wrap_neg",
    "forward_4",
    "block_scale_dev",
)
AB_NOMINAL = 3239.77
CONTRACT = "1-1-tune-proxy-v2"
BACKEND = "1_1_tune"
PROXY_ID = "1_1_tune_v2"
SWAPPED_WALK = ["K", "B1", "A2", "A1", "A3", "B2"]
REPLAY_SOURCES = {
    "a02_proud_on_a01": "a01_mirror_k",
    "a05_proud3_on_a01": "a01_mirror_k",
    "a21_a2_over_a1": "a17_angle_650",
    "a22_a2_bias_2": "a17_angle_650",
    "a23_a2_over_a1_on_a17": "a17_angle_650",
    "a29_a1_over_b1_on_a17": "a17_angle_650",
    "a34_ring2_label_shift": "a17_angle_650",
    "a38_a34_proud_r10_5mm": "a34_ring2_label_shift",
    "a39_a34_proud_r15_5mm": "a34_ring2_label_shift",
    "a40_a34_proud_r20_5mm": "a34_ring2_label_shift",
    "a41_a34_proud_r10_6mm": "a34_ring2_label_shift",
    "a42_a34_proud_r07_4mm": "a34_ring2_label_shift",
}


def features_from_pack(sam: dict, denoising: dict | None = None) -> dict[str, float]:
    denoise = denoising or {}
    shifts = sam.get("ring_label_shifts") or {}
    split = sam.get("ring_theta_split") or {}
    scales = sam.get("block_template_scale") or {}
    residual = sam.get("proud_residual_mm")
    proud_mm = 0.0 if residual is None else float(residual)
    template = 1.0 if sam.get("template_scale") is None else float(sam["template_scale"])
    mask_low = float(denoise.get("mask_r_low", 2.32))
    ab = float(sam.get("AB_height", AB_NOMINAL))
    a1 = float(scales.get("A1", 1.0))
    a2 = float(scales.get("A2", 1.0))
    dark = sam.get("dark_lining_below")
    values = {
        "proud_mm": proud_mm,
        "mid_mask": 1.0 if mask_low >= 2.70 else 0.0,
        "ring2_shift": 1.0 if int(shifts.get("2", 0) or 0) == 1 else 0.0,
        "theta_split": 1.0 if _theta_split(split) else 0.0,
        "dark_m1400": 1.0 if dark == -1400 else 0.0,
        "wrap_theta": 1.0 if sam.get("wrap_theta") else 0.0,
        "ab_rel_error": abs(ab - AB_NOMINAL) / AB_NOMINAL,
        "scale_dev": abs(template - 1.0),
        "walk_swapped": 1.0 if sam.get("circumferential_block_order") == SWAPPED_WALK else 0.0,
        "mask_off": 1.0 if sam.get("use_template_mask_input") is False else 0.0,
        "a1_wrap_neg": 1.0 if sam.get("a1_wrap_negative_prompts") else 0.0,
        "forward_4": 1.0 if sam.get("min_forward_blocks") == 4 else 0.0,
        "block_scale_dev": max(abs(a1 - 1.0), abs(a2 - 1.0)),
    }
    return {key: float(values[key]) for key in FEATURE_IDS}


def _theta_split(split: dict) -> bool:
    theta = split.get("theta")
    return (
        split.get("ring") == 2
        and split.get("source_label") == 6
        and theta is not None
        and float(theta) == 12.4
        and split.get("below_label") == 2
        and split.get("at_or_above_label") == 1
    )


def load_tune_rows(tune_root: Path) -> tuple[DevelopmentRow, ...]:
    tune_root = Path(tune_root)
    params_root = tune_root / "params"
    packs = {}
    for pack in sorted(path for path in params_root.iterdir() if path.is_dir()):
        maps = {path.name: json.loads(path.read_text()) for path in pack.glob("*.json")}
        packs[pack.name] = features_from_pack(
            maps.get("parameters_sam.json", {}),
            maps.get("parameters_denoising.json"),
        )
    pending = [name for name in REPLAY_SOURCES if name not in packs]
    while pending:
        advanced = False
        for name in list(pending):
            source = REPLAY_SOURCES[name]
            if source not in packs:
                continue
            packs[name] = _replay_features(tune_root, name, packs[source])
            pending.remove(name)
            advanced = True
        if not advanced:
            raise ValueError("unresolved_replay:" + ",".join(pending))
    arms = sorted(
        path.name for path in tune_root.iterdir() if path.is_dir() and path.name != "params"
    )
    missing = [name for name in arms if name not in packs]
    if missing:
        raise ValueError("missing_tune_features:" + ",".join(missing))
    return tuple(
        DevelopmentRow(
            "1-1",
            "1-1",
            name,
            tuple((key, packs[name][key]) for key in FEATURE_IDS),
            _read_miou(tune_root, name),
            False,
        )
        for name in arms
    )


def _replay_features(tune_root: Path, name: str, source: dict[str, float]) -> dict[str, float]:
    features = dict(source)
    if name == "a02_proud_on_a01":
        features["proud_mm"] = 5.0
    elif name == "a05_proud3_on_a01":
        features["proud_mm"] = 3.0
    elif name == "a34_ring2_label_shift":
        features["ring2_shift"] = 1.0
    elif name in {
        "a38_a34_proud_r10_5mm",
        "a39_a34_proud_r15_5mm",
        "a40_a34_proud_r20_5mm",
        "a41_a34_proud_r10_6mm",
        "a42_a34_proud_r07_4mm",
    }:
        result = json.loads((tune_root / f"{name}_result.json").read_text())
        features["proud_mm"] = float(result["proud_residual_mm"])
    return {key: float(features[key]) for key in FEATURE_IDS}


def _read_miou(tune_root: Path, name: str) -> float:
    result = tune_root / f"{name}_result.json"
    if result.is_file():
        value = float(json.loads(result.read_text())["mIoU"])
    else:
        text = (tune_root / name / "evaluation" / "performance.md").read_text()
        value = next(float(line.split(":")[-1]) for line in text.splitlines() if "Mean IoU" in line)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"invalid_miou:{name}")
    return value


def fit_one_one_proxy(rows: tuple[DevelopmentRow, ...]) -> FrozenProxy:
    return fit_proxy(
        rows,
        FEATURE_IDS,
        proxy_id=PROXY_ID,
        evidence_contract_digest=CONTRACT,
        backend=BACKEND,
    )


def proxy_record(rows: tuple[DevelopmentRow, ...] | None = None, proxy: FrozenProxy | None = None) -> dict:
    fitted_rows = rows if rows is not None else load_tune_rows(Path("data/development/1-1/tune"))
    fitted = proxy or fit_one_one_proxy(fitted_rows)
    scores = [
        fitted.predict(dict(row.features), CONTRACT, BACKEND)
        for row in fitted_rows
    ]
    best = max(range(len(fitted_rows)), key=lambda index: scores[index])
    return {
        "proxy_id": fitted.proxy_id,
        "target": "final_3d_semantic_miou",
        "status": "development_fit_pending",
        "scope": {
            "family": "staggered",
            "scan": "data/scans/1-1.txt",
            "case_id": "1-1",
            "group_id": "1-1",
            "rows": "data/development/1-1/tune",
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
        "n_rows": len(fitted_rows),
        "in_sample_mae": float(mean(abs(score - row.final_miou) for score, row in zip(scores, fitted_rows))),
        "best_run_id": fitted_rows[best].run_id,
        "best_observed_miou": fitted_rows[best].final_miou,
        "best_proxy_score": scores[best],
        "equation": "clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)",
        "notes": (
            "Development fit on every arm in data/development/1-1/tune, including a45. "
            "The K mirror is on in every row. "
            "dark_m1400 is the -1400 cut. theta_split is ring 2, source 6, theta 12.4. "
            "ring2_shift is +1 on ring 2. "
            "One scan. Not a released proxy. Not accepted wisdom."
        ),
    }
