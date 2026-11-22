from __future__ import annotations

import numpy as np


def split_ring_source_by_theta(
    labels,
    source_labels,
    rings,
    theta,
    *,
    ring,
    source_label,
    theta_cut,
    below_label,
    at_or_above_label,
):
    out = np.array(labels, copy=True)
    selected = (np.asarray(rings) == int(ring)) & (np.asarray(source_labels) == int(source_label))
    theta = np.asarray(theta, dtype=float)
    out[selected & (theta < float(theta_cut))] = int(below_label)
    out[selected & (theta >= float(theta_cut))] = int(at_or_above_label)
    return out
