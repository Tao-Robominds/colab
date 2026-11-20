from dataclasses import dataclass

from rsi4tun.contracts import CompletedRun


@dataclass(frozen=True)
class MiouReport:
    final_miou: float
    per_class_iou: tuple[tuple[int, float | None], ...]
    evaluated_points: int
    absent_policy: str = "exclude_union_empty"


def evaluate_miou(run: CompletedRun, truth_by_point: dict[int, int], *,
                  class_ids: tuple[int, ...], ignore_gt_label: int | None = None,
                  unassigned_prediction: int = -1) -> MiouReport:
    run.require_complete()
    if not class_ids or len(set(class_ids)) != len(class_ids):
        raise ValueError("invalid_semantic_class_schema")
    if unassigned_prediction in class_ids or ignore_gt_label in class_ids:
        raise ValueError("invalid_semantic_sentinel")
    if set(truth_by_point) != set(run.point_ids):
        raise ValueError("point_identity_mismatch")
    pairs = []
    for point_id, predicted in zip(run.point_ids, run.predicted_labels):
        actual = truth_by_point[point_id]
        if actual == ignore_gt_label:
            continue
        if actual not in class_ids or predicted not in (*class_ids, unassigned_prediction):
            raise ValueError("unknown_semantic_label")
        pairs.append((actual, predicted))
    if not pairs:
        raise ValueError("no_evaluable_points")
    per_class = []
    for label in class_ids:
        intersection = sum(actual == label and predicted == label for actual, predicted in pairs)
        union = sum(actual == label or predicted == label for actual, predicted in pairs)
        per_class.append((label, intersection / union if union else None))
    values = [value for _, value in per_class if value is not None]
    return MiouReport(sum(values) / len(values), tuple(per_class), len(pairs))
