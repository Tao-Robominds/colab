import numpy as np
from scipy.spatial import cKDTree


def drop_proud_lining(h, theta, radius, pred, neighbourhood_m, residual_m):
    pred = np.asarray(pred).copy()
    h = np.asarray(h, dtype=np.float64)
    theta = np.asarray(theta, dtype=np.float64)
    radius = np.asarray(radius, dtype=np.float64)
    lining = np.flatnonzero((pred >= 1) & (pred <= 6))
    if len(lining) == 0:
        return pred
    period = float(2 * np.pi * np.median(radius))
    xy = np.column_stack([h[lining], theta[lining]])
    shift = np.full(len(lining), period)
    stacked = np.vstack([
        xy,
        np.column_stack([xy[:, 0], xy[:, 1] + shift]),
        np.column_stack([xy[:, 0], xy[:, 1] - shift]),
    ])
    values = np.concatenate([radius[lining], radius[lining], radius[lining]])
    tree = cKDTree(stacked)
    count = len(lining)
    neighbours = tree.query_ball_point(xy, neighbourhood_m)
    for index, found in enumerate(neighbours):
        others = [
            values[item]
            for item in found
            if item != index and item != index + count and item != index + 2 * count
        ]
        if not others:
            continue
        if radius[lining[index]] - float(np.median(others)) > residual_m:
            pred[lining[index]] = 0
    return pred
