from __future__ import annotations

import numpy as np


def drop_dark_lining(labels, intensity, below):
    out = np.array(labels, copy=True)
    intensity = np.asarray(intensity, dtype=float)
    lining = (out >= 1) & (out <= 6)
    out[lining & (intensity < float(below))] = 0
    return out
