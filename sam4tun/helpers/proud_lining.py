import numpy as np
from scipy.spatial import cKDTree

QUERY_CHUNK = 256


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
    lining_radius = radius[lining]
    for start in range(0, count, QUERY_CHUNK):
        stop = min(start + QUERY_CHUNK, count)
        batches = tree.query_ball_point(xy[start:stop], neighbourhood_m, return_sorted=False)
        for offset, found in enumerate(batches):
            index = start + offset
            if len(found) <= 1:
                continue
            ids = np.fromiter(found, dtype=np.int64, count=len(found))
            keep = (ids != index) & (ids != index + count) & (ids != index + 2 * count)
            if not keep.any():
                continue
            if lining_radius[index] - float(np.median(values[ids[keep]])) > residual_m:
                pred[lining[index]] = 0
    return pred
