from __future__ import annotations

import numpy as np


def crop_image_theta(image, cx, cy, crop_width, crop_height, *, wrap_theta: bool = False):
    img_height, img_width = image.shape[:2]
    half_w = crop_width // 2
    half_h = crop_height // 2
    x1 = int(cx - half_w)
    x2 = int(cx + half_w)
    y1 = int(cy - half_h)
    y2 = int(cy + half_h)

    x1_c = max(x1, 0)
    x2_c = min(x2, img_width)

    if wrap_theta:
        rows = np.arange(y1, y1 + crop_height) % img_height
        cropped = image[rows][:, x1_c:x2_c]
        prompt_centre = (cx - x1_c, cy - y1)
        origin = (float(x1_c), float(y1))
        return cropped, prompt_centre, origin

    y1_c = max(y1, 0)
    y2_c = min(y2, img_height)
    cropped = image[y1_c:y2_c, x1_c:x2_c]
    prompt_centre = (cx - x1_c, cy - y1_c)
    origin = (float(x1_c), float(y1_c))
    return cropped, prompt_centre, origin


def wrap_prompt_y(points, labels, crop_height, *, wrap_theta: bool = False):
    points = np.asarray(points, dtype=float)
    labels = np.asarray(labels)
    if points.size == 0:
        return points, labels
    if wrap_theta:
        wrapped = points.copy()
        wrapped[:, 1] = np.mod(wrapped[:, 1], crop_height)
        return wrapped, labels
    keep = (points[:, 1] >= 0) & (points[:, 1] < crop_height)
    return points[keep], labels[keep]


def paste_patch_theta(
    logits_map,
    label_map,
    ring_map,
    mask,
    new_logits,
    label,
    ring_index,
    start_x,
    start_y,
    *,
    wrap_theta: bool = False,
):
    height, width = logits_map.shape
    mask = np.asarray(mask, dtype=bool)
    new_logits = np.asarray(new_logits)
    if mask.shape != new_logits.shape:
        raise ValueError("paste_shape_mismatch")
    mh, mw = mask.shape
    if wrap_theta:
        rows = (np.arange(start_y, start_y + mh) % height).astype(int)
        cols = np.arange(start_x, start_x + mw)
        valid_cols = (cols >= 0) & (cols < width)
        cols = cols[valid_cols]
        if cols.size == 0:
            return
        mask_x = mask[:, valid_cols]
        logits_x = new_logits[:, valid_cols]
        current = logits_map[np.ix_(rows, cols)]
        update = (logits_x > current) & mask_x
        logits_map[np.ix_(rows, cols)] = np.where(update, logits_x, current)
        label_map[np.ix_(rows, cols)] = np.where(update, label, label_map[np.ix_(rows, cols)])
        ring_map[np.ix_(rows, cols)] = np.where(update, ring_index, ring_map[np.ix_(rows, cols)])
        return

    y1 = max(start_y, 0)
    x1 = max(start_x, 0)
    y2 = min(start_y + mh, height)
    x2 = min(start_x + mw, width)
    if y1 >= y2 or x1 >= x2:
        return
    my1 = y1 - start_y
    mx1 = x1 - start_x
    my2 = my1 + (y2 - y1)
    mx2 = mx1 + (x2 - x1)
    sub_mask = mask[my1:my2, mx1:mx2]
    sub_logits = new_logits[my1:my2, mx1:mx2]
    current = logits_map[y1:y2, x1:x2]
    update = (sub_logits > current) & sub_mask
    logits_map[y1:y2, x1:x2][update] = sub_logits[update]
    label_map[y1:y2, x1:x2][update] = label
    ring_map[y1:y2, x1:x2][update] = ring_index
