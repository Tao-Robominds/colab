"""Two-pass fill for assume centres from measured centres on the same scan.

Measured rows keep their Y. Each assume takes the Y of the nearest measured
centre with the same ring-index parity. Defaults stay off in detecting params;
callers must enable ``assume_parity_fill``.
"""
from __future__ import annotations

from typing import Iterable, Sequence

MEASURED_TYPES = frozenset(
    {"midpoint", "horizontal", "positive_slope", "negative_slope"}
)


def fill_assumes_from_parity_measured(
    points: Sequence[tuple[str, tuple[float, float]]],
) -> list[tuple[str, tuple[float, float]]]:
    """Replace assume Y with nearest same-parity measured Y; leave others.

    ``points`` are ``(type, (x, y))`` in ring order (left to right). Measured
    types are midpoint / horizontal / positive_slope / negative_slope.
    """
    measured: list[tuple[int, float, float]] = []
    for idx, (label, (x, y)) in enumerate(points):
        if label in MEASURED_TYPES:
            measured.append((idx, float(x), float(y)))

    out: list[tuple[str, tuple[float, float]]] = []
    for idx, (label, (x, y)) in enumerate(points):
        if label != "assume":
            out.append((label, (float(x), float(y))))
            continue
        same = [row for row in measured if row[0] % 2 == idx % 2]
        if not same:
            out.append((label, (float(x), float(y))))
            continue
        _j, _mx, my = min(same, key=lambda row: abs(row[1] - float(x)))
        out.append((label, (float(x), float(my))))
    return out


def points_from_rows(rows: Iterable[dict[str, object]]) -> list[tuple[str, tuple[float, float]]]:
    """Build ``(type, (x, y))`` from CSV-like row dicts with Type/X/Y."""
    return [
        (str(row["Type"]), (float(row["X"]), float(row["Y"])))
        for row in rows
    ]
