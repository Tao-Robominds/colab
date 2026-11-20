"""Default-off K-centre repairs for staggered detection.

Each function takes ``(type, (x, y))`` rows in ring order and returns a new list.
Callers enable them from ``parameters_detecting.json``; nothing runs by default.
"""
from __future__ import annotations

from typing import Callable, Sequence

MEASURED_TYPES = frozenset(
    {"midpoint", "horizontal", "positive_slope", "negative_slope"}
)
SLOPE_TYPES = frozenset({"positive_slope", "negative_slope"})
Point = tuple[str, tuple[float, float]]


def farthest_nonassume_band(
    points: Sequence[Point],
) -> list[Point]:
    """Sandwiched assume takes the measured Y farthest from its neighbour mean."""
    baseline = list(points)
    nonassume_ys = [
        float(coord[1])
        for label, coord in baseline
        if label in MEASURED_TYPES
    ]
    repaired: list[Point] = []
    for idx, (label, coord) in enumerate(baseline):
        if label != "assume" or not nonassume_ys:
            repaired.append((label, (float(coord[0]), float(coord[1]))))
            continue
        left = baseline[idx - 1] if idx > 0 else None
        right = baseline[idx + 1] if idx + 1 < len(baseline) else None
        if left is None or right is None or left[0] != "assume" or right[0] != "assume":
            repaired.append((label, (float(coord[0]), float(coord[1]))))
            continue
        neighbor_mean = 0.5 * (float(left[1][1]) + float(right[1][1]))
        chosen_y = max(nonassume_ys, key=lambda y: abs(y - neighbor_mean))
        repaired.append(("assume", (float(coord[0]), float(chosen_y))))
    return repaired


def other_slope_median(
    points: Sequence[Point],
    *,
    threshold_px: float = 600.0,
) -> list[Point]:
    """Replace a slope Y that is far from the median of the other slopes."""
    baseline = list(points)
    slope_idxs = [i for i, (label, _) in enumerate(baseline) if label in SLOPE_TYPES]
    repaired: list[Point] = [
        (label, (float(coord[0]), float(coord[1]))) for label, coord in baseline
    ]
    if len(slope_idxs) < 2:
        return repaired
    for i in slope_idxs:
        label, coord = baseline[i]
        other_ys = [float(baseline[j][1][1]) for j in slope_idxs if j != i]
        other_median = sum(other_ys) / len(other_ys)
        # Use true median for odd/even counts.
        other_sorted = sorted(other_ys)
        mid = len(other_sorted) // 2
        if len(other_sorted) % 2:
            other_median = float(other_sorted[mid])
        else:
            other_median = 0.5 * (other_sorted[mid - 1] + other_sorted[mid])
        if abs(float(coord[1]) - other_median) > float(threshold_px):
            repaired[i] = (label, (float(coord[0]), float(other_median)))
    return repaired


def lone_slope_to_nonassume(
    points: Sequence[Point],
) -> list[Point]:
    """If exactly one slope remains, reclassify it using a non-assume Y band."""
    baseline = list(points)
    slope_idxs = [i for i, (label, _) in enumerate(baseline) if label in SLOPE_TYPES]
    repaired: list[Point] = [
        (label, (float(coord[0]), float(coord[1]))) for label, coord in baseline
    ]
    if len(slope_idxs) != 1:
        return repaired
    i = slope_idxs[0]
    _label, coord = baseline[i]
    nonassume_ys = [
        float(c[1])
        for lab, c in baseline
        if lab in ("midpoint", "horizontal")
    ]
    if not nonassume_ys:
        return repaired
    left = baseline[i - 1] if i > 0 else None
    right = baseline[i + 1] if i + 1 < len(baseline) else None
    if left is not None and right is not None:
        neighbor_mean = 0.5 * (float(left[1][1]) + float(right[1][1]))
        chosen_y = max(nonassume_ys, key=lambda y: abs(y - neighbor_mean))
    else:
        chosen_y = sorted(nonassume_ys)[len(nonassume_ys) // 2]
    repaired[i] = ("midpoint", (float(coord[0]), float(chosen_y)))
    return repaired


def horizontal_if_pattern(
    points: Sequence[Point],
    *,
    pattern_at_x: Callable[[float], tuple[float, float] | None],
) -> list[Point]:
    """Replace a single-slope centre with a horizontal pattern midpoint when present.

    ``pattern_at_x(x)`` returns ``(x, y)`` of the pattern midpoint, or None.
    """
    repaired: list[Point] = []
    for label, coord in points:
        if label not in SLOPE_TYPES:
            repaired.append((label, (float(coord[0]), float(coord[1]))))
            continue
        mid = pattern_at_x(float(coord[0]))
        if mid is None:
            repaired.append((label, (float(coord[0]), float(coord[1]))))
        else:
            repaired.append(("horizontal", (float(mid[0]), float(mid[1]))))
    return repaired


def _median(values: Sequence[float]) -> float:
    ordered = sorted(float(v) for v in values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def assume_from_measured_parity(points: Sequence[Point]) -> list[Point]:
    """A missed ring takes the median Y of measured centres with the same index parity."""
    even: list[float] = []
    odd: list[float] = []
    for idx, (label, coord) in enumerate(points):
        if label not in MEASURED_TYPES:
            continue
        (even if idx % 2 == 0 else odd).append(float(coord[1]))
    repaired: list[Point] = []
    for idx, (label, coord) in enumerate(points):
        x, y = float(coord[0]), float(coord[1])
        if label != "assume":
            repaired.append((label, (x, y)))
            continue
        pool = even if idx % 2 == 0 else odd
        if not pool:
            repaired.append((label, (x, y)))
            continue
        repaired.append(("assume", (x, _median(pool))))
    return repaired


def assume_on_edge(points: Sequence[Point], edge_y: float) -> list[Point]:
    """Place every assume centre on one measured edge, with no half-K offset."""
    repaired: list[Point] = []
    for label, coord in points:
        x, y = float(coord[0]), float(coord[1])
        if label == "assume":
            repaired.append(("assume", (x, float(edge_y))))
        else:
            repaired.append((label, (x, y)))
    return repaired


def count_changed(before: Sequence[Point], after: Sequence[Point]) -> int:
    n = 0
    for (la, (xa, ya)), (lb, (xb, yb)) in zip(before, after):
        if la != lb or abs(float(ya) - float(yb)) > 1e-6 or abs(float(xa) - float(xb)) > 1e-6:
            n += 1
    return n
