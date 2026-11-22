from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class CropRow:
    ring: int
    block: str
    area: int
    full_area: int
    area_ratio: float
    touches_top: bool
    touches_bottom: bool
    depth_validity: float
    positive_prompts: int
    negative_prompts: int
    score: float
    origin_y: float
    origin_x: float
    height: int
    width: int


@dataclass(frozen=True)
class DiagnosisReport:
    rows: tuple[CropRow, ...]
    seam_open: bool
    seam_blocks: tuple[str, ...]
    border_area_ratio: float
    complete_low_score: tuple[CropRow, ...]
    depth_margin: tuple[CropRow, ...]
    mask_fight_pixels: int


def load_arm_artifacts(arm_dir: Path) -> tuple[list, np.ndarray]:
    arm_dir = Path(arm_dir)
    with (arm_dir / "results.pkl").open("rb") as handle:
        results = pickle.load(handle)
    depth = np.load(arm_dir / "depth_map.npy")
    return results, depth


def _mask_array(item: dict[str, Any]) -> np.ndarray:
    mask = np.asarray(item["mask"])
    if mask.ndim == 3:
        mask = mask[0]
    return mask.astype(bool)


def _score_value(item: dict[str, Any]) -> float:
    score = np.asarray(item["score"]).reshape(-1)
    if score.size == 0:
        return float("nan")
    return float(score[0])


def _prompt_counts(item: dict[str, Any]) -> tuple[int, int]:
    labels = np.asarray(item["labels"])
    return int((labels == 1).sum()), int((labels == 0).sum())


def crop_rows_from_results(results: list, depth: np.ndarray) -> tuple[CropRow, ...]:
    height, width = depth.shape[:2]
    full_area: dict[str, int] = {}
    for ring in results:
        for item in ring:
            area = int(_mask_array(item).size)
            block = str(item["block"])
            if area > full_area.get(block, 0):
                full_area[block] = area

    valid = np.isfinite(depth) & (depth != 0)
    rows: list[CropRow] = []
    for ring_index, ring in enumerate(results):
        for item in ring:
            mask = _mask_array(item)
            x0 = int(round(float(item["left_top"][0])))
            y0 = int(round(float(item["left_top"][1])))
            y1 = y0 + mask.shape[0]
            x1 = x0 + mask.shape[1]
            ys = max(0, y0)
            ye = min(height, y1)
            xs = max(0, x0)
            xe = min(width, x1)
            if ye <= ys or xe <= xs:
                depth_validity = 0.0
            else:
                mm = mask[(ys - y0):(ye - y0), (xs - x0):(xe - x0)]
                sub = valid[ys:ye, xs:xe]
                if mm.shape != sub.shape or not mm.any():
                    depth_validity = 0.0
                else:
                    depth_validity = float(sub[mm].mean())
            pos, neg = _prompt_counts(item)
            area = int(mask.size)
            block = str(item["block"])
            denom = max(full_area.get(block, area), 1)
            rows.append(
                CropRow(
                    ring=ring_index,
                    block=block,
                    area=area,
                    full_area=denom,
                    area_ratio=area / denom,
                    touches_top=y0 <= 0,
                    touches_bottom=y1 >= height,
                    depth_validity=depth_validity,
                    positive_prompts=pos,
                    negative_prompts=neg,
                    score=_score_value(item),
                    origin_y=float(y0),
                    origin_x=float(x0),
                    height=int(mask.shape[0]),
                    width=int(mask.shape[1]),
                )
            )
    return tuple(rows)


def _interior_prompt_count(rows: tuple[CropRow, ...]) -> int:
    interior = [
        row.positive_prompts
        for row in rows
        if row.area_ratio >= 0.85 and not row.touches_top and not row.touches_bottom
    ]
    if not interior:
        return 0
    return int(max(interior))


def classify_crops(
    rows: tuple[CropRow, ...],
    *,
    seam_area_max: float = 0.45,
    low_score_max: float = 0.75,
    depth_margin_max: float = 0.75,
) -> DiagnosisReport:
    if not rows:
        return DiagnosisReport((), False, (), 1.0, (), (), 0)

    scores = [row.score for row in rows if np.isfinite(row.score)]
    score_high = max(scores) if scores else 1.0
    interior_prompts = _interior_prompt_count(rows)
    prompt_cut = max(int(interior_prompts * 0.5), 20) if interior_prompts else 20

    seam_rows = []
    for row in rows:
        on_border = row.touches_top or row.touches_bottom
        if not on_border:
            continue
        if row.area_ratio > seam_area_max:
            continue
        if row.score < score_high - 0.05:
            continue
        if interior_prompts and row.positive_prompts > prompt_cut:
            continue
        seam_rows.append(row)

    complete_low = tuple(
        row
        for row in rows
        if row.area_ratio >= 0.85
        and row.depth_validity >= 0.9
        and row.score <= low_score_max
    )
    depth_margin = tuple(
        row
        for row in seam_rows
        if row.depth_validity < depth_margin_max
    )
    if seam_rows:
        border_area_ratio = min(row.area_ratio for row in seam_rows)
    else:
        border = [row for row in rows if row.touches_top or row.touches_bottom]
        border_area_ratio = min((row.area_ratio for row in border), default=1.0)

    seam_blocks = tuple(sorted({row.block for row in seam_rows}))
    return DiagnosisReport(
        rows=rows,
        seam_open=bool(seam_rows),
        seam_blocks=seam_blocks,
        border_area_ratio=float(border_area_ratio),
        complete_low_score=complete_low,
        depth_margin=depth_margin,
        mask_fight_pixels=0,
    )


def summarize_vector(report: DiagnosisReport) -> dict:
    return {
        "seam_open": report.seam_open,
        "seam_blocks": list(report.seam_blocks),
        "border_area_ratio": report.border_area_ratio,
        "complete_low_score": [
            {
                "ring": row.ring,
                "block": row.block,
                "score": row.score,
                "area_ratio": row.area_ratio,
            }
            for row in report.complete_low_score
        ],
        "depth_margin": [
            {
                "ring": row.ring,
                "block": row.block,
                "depth_validity": row.depth_validity,
                "area_ratio": row.area_ratio,
            }
            for row in report.depth_margin
        ],
        "mask_fight_pixels": report.mask_fight_pixels,
        "n_crops": len(report.rows),
    }


def diagnose_arm(arm_dir: Path) -> DiagnosisReport:
    results, depth = load_arm_artifacts(arm_dir)
    return classify_crops(crop_rows_from_results(results, depth))


def compare_sealed_pattern(
    sealed: dict,
    report: DiagnosisReport,
    *,
    baseline_miou: float,
    observed_miou: float,
    tolerance: float = 0.01,
) -> str:
    predicted = sealed.get("predicted_border_area_ratio")
    border_filled = report.border_area_ratio >= 0.8
    miou_moved = abs(observed_miou - baseline_miou) > tolerance
    if predicted is not None and float(predicted) >= 0.8 and not border_filled:
        return "treatment_failed"
    if border_filled and not miou_moved:
        return "metric_not_target"
    if border_filled and miou_moved:
        return "both_moved"
    return "treatment_failed"
