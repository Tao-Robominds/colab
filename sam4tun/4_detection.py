#!/usr/bin/env python3
import sys
import os
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from helpers.pipeline_io import ensure_dir
from helpers.pipeline_state import load_state, save_state
tunnel_id = sys.argv[1]
paths = ensure_dir(tunnel_id)
state = load_state(paths['state'])
df_point_cloud = state['df_point_cloud']
df_enhance_segment = state['df_enhance_segment']
df_enhance_joint = state['df_enhance_joint']
ring_count = state['ring_count']
resolution = state.get('resolution', 0.005)
depth_map_outlier = state['depth_map_outlier']
import cv2
binary_map = np.where(np.isnan(depth_map_outlier), 0, 255).astype(np.uint8)
ret, binary_image = cv2.threshold(binary_map, 127, 255, cv2.THRESH_BINARY)
kernel = np.ones((3, 3), np.uint8)
dilated_edges = cv2.dilate(binary_image, kernel, iterations=1)
import cv2
import numpy as np
import matplotlib.pyplot as plt
L, W = binary_map.shape

def _hough_p_as_nx1x4(lines):
    if lines is None:
        return None
    arr = np.asarray(lines)
    if arr.ndim == 2 and arr.shape[1] == 4:
        return arr.reshape(-1, 1, 4)
    return arr
lines_oblique = _hough_p_as_nx1x4(cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=40))
lines_horizontal = _hough_p_as_nx1x4(cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=10))
lines_vertical = cv2.HoughLines(dilated_edges, 1, np.pi / 180, 500)
lines_vertical_all = lines_vertical
if lines_vertical is not None:
    lines_vertical_filtered = lines_vertical[lines_vertical[:, 0, 0] <= 5 * 1200 / (resolution * 1000)]
    if len(lines_vertical_filtered) > 0:
        lines_vertical = lines_vertical_filtered
output_image = cv2.cvtColor(dilated_edges, cv2.COLOR_GRAY2BGR)
color_angle1 = (255, 0, 0)
color_angle2 = (0, 255, 0)
color_horizontal = (0, 0, 255)
color_vertical = (255, 165, 0)
color_mid_lines = (255, 0, 255)
line_thickness = 3
joint_oblique_positive = []
joint_oblique_negtive = []
joint_horizontal = []
if lines_oblique is not None:
    for line in lines_oblique:
        x1, y1, x2, y2 = line[0]
        x1, x2, y1, y2 = (x2, x1, y2, y1) if x1 > x2 else (x1, x2, y1, y2)
        angle = np.degrees(np.arctan2(-(y2 - y1), x2 - x1))
        if 6 <= angle <= 9:
            joint_oblique_positive.append(line)
            cv2.line(output_image, (x1, y1), (x2, y2), color_angle1, line_thickness)
        elif -9 <= angle <= -6:
            joint_oblique_negtive.append(line)
            cv2.line(output_image, (x1, y1), (x2, y2), color_angle2, line_thickness)
if lines_horizontal is not None:
    for line in lines_horizontal:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -1 <= angle <= 1:
            joint_horizontal.append(line)
            cv2.line(output_image, (x1, y1), (x2, y2), color_horizontal, line_thickness)
merged_lines = []
all_mid_lines = []
threshold_distance = 3
if lines_vertical is not None:
    lines_vertical = lines_vertical[:, 0]
    for i, (rho1, theta1) in enumerate(lines_vertical):
        if -0.5 * np.pi / 180 <= abs(theta1) <= 0.5 * np.pi / 180:
            x1, y1 = (rho1 * np.cos(theta1), rho1 * np.sin(theta1))
            is_merged = False
            for j, (rho2, theta2) in enumerate(merged_lines):
                x2, y2 = (rho2 * np.cos(theta2), rho2 * np.sin(theta2))
                if np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < threshold_distance:
                    new_rho = (rho1 + rho2) / 2
                    new_theta = (theta1 + theta2) / 2
                    merged_lines[j] = (new_rho, new_theta)
                    is_merged = True
                    break
            if not is_merged:
                merged_lines.append((rho1, theta1))
    merged_lines.sort(key=lambda line: line[0])
    for rho, theta in merged_lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 2677 * -b)
        y1 = int(y0 + 2677 * a)
        x2 = int(x0 - 2677 * -b)
        y2 = int(y0 - 2677 * a)
        cv2.line(output_image, (x1, y1), (x2, y2), color_vertical, line_thickness)
    mid_lines = []
    num_lines = len(merged_lines)
    for i in range(num_lines - 1):
        rho1, theta1 = merged_lines[i]
        rho2, theta2 = merged_lines[i + 1]
        new_rho = (rho1 + rho2) / 2
        new_theta = (theta1 + theta2) / 2
        mid_lines.append((new_rho, new_theta))
        a = np.cos(new_theta)
        b = np.sin(new_theta)
        x0 = a * new_rho
        y0 = b * new_rho
        x1 = int(x0 + L * -b)
        y1 = int(y0 + L * a)
        x2 = int(x0 - L * -b)
        y2 = int(y0 - L * a)
        cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)
    distances = []
    for i in range(len(mid_lines) - 1):
        rho1, theta1 = mid_lines[i]
        rho2, theta2 = mid_lines[i + 1]
        x1, y1 = (rho1 * np.cos(theta1), rho1 * np.sin(theta1))
        x2, y2 = (rho2 * np.cos(theta2), rho2 * np.sin(theta2))
        distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        distances.append(distance)
    avg_distance_detected = np.mean(distances) if distances else 0
    avg_distance_designed = W / ring_count
    if np.abs(avg_distance_detected - 1.2 / resolution) <= np.abs(avg_distance_designed - 1.2 / resolution):
        avg_distance = avg_distance_detected
    else:
        avg_distance = avg_distance_designed
    all_mid_lines = mid_lines.copy()
    if mid_lines:
        leftmost_rho, leftmost_theta = mid_lines[0]
        a = np.cos(leftmost_theta)
        b = np.sin(leftmost_theta)
        x0 = a * leftmost_rho
        y0 = b * leftmost_rho
        while x0 >= 0:
            x1 = int(x0 + L * -b)
            y1 = int(y0 + L * a)
            x2 = int(x0 - L * -b)
            y2 = int(y0 - L * a)
            cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)
            all_mid_lines.append((x0, leftmost_theta))
            x0 -= avg_distance
        rightmost_rho, rightmost_theta = mid_lines[-1]
        a = np.cos(rightmost_theta)
        b = np.sin(rightmost_theta)
        x0 = a * rightmost_rho
        y0 = b * rightmost_rho
        while x0 <= output_image.shape[1]:
            x1 = int(x0 + L * -b)
            y1 = int(y0 + L * a)
            x2 = int(x0 - L * -b)
            y2 = int(y0 - L * a)
            cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)
            all_mid_lines.append((x0, rightmost_theta))
            x0 += avg_distance
all_mid_lines = sorted(list(set(all_mid_lines)), key=lambda line: line[0])
if (lines_vertical is None or len(all_mid_lines) == 0) and lines_vertical_all is not None:
    lines_vertical = lines_vertical_all[:, 0]
    merged_lines = []
    all_mid_lines = []
    for rho1, theta1 in lines_vertical:
        if -0.5 * np.pi / 180 <= abs(theta1) <= 0.5 * np.pi / 180:
            merged_lines.append((rho1, theta1))
    merged_lines.sort(key=lambda line: line[0])
    mid_lines = []
    for i in range(len(merged_lines) - 1):
        rho1, theta1 = merged_lines[i]
        rho2, theta2 = merged_lines[i + 1]
        mid_lines.append(((rho1 + rho2) / 2, (theta1 + theta2) / 2))
    avg_distance = W / ring_count
    all_mid_lines = mid_lines.copy()
    if mid_lines:
        leftmost_rho, leftmost_theta = mid_lines[0]
        a, b = (np.cos(leftmost_theta), np.sin(leftmost_theta))
        x0 = a * leftmost_rho
        while x0 >= 0:
            all_mid_lines.append((x0, leftmost_theta))
            x0 -= avg_distance
        rightmost_rho, rightmost_theta = mid_lines[-1]
        a, b = (np.cos(rightmost_theta), np.sin(rightmost_theta))
        x0 = a * rightmost_rho
        while x0 <= W:
            all_mid_lines.append((x0, rightmost_theta))
            x0 += avg_distance
    all_mid_lines = sorted(list(set(all_mid_lines)), key=lambda line: line[0])
if len(all_mid_lines) > 0:
    targets = [(i + 0.5) * W / ring_count for i in range(ring_count)]
    remaining = sorted(list(set(all_mid_lines)), key=lambda line: line[0])
    selected = []
    for tx in targets:
        if not remaining:
            break
        best = min(remaining, key=lambda line: abs(line[0] - tx))
        selected.append(best)
        remaining.remove(best)
    all_mid_lines = selected
plt.figure(figsize=(12, 12))
plt.imshow(output_image)
plt.axis('off')
plt.savefig(paths['detected_lines'], dpi=150, bbox_inches='tight')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def line_segment_vertical_intersection(vertical_x, segment):
    x1, y1, x2, y2 = segment
    if x1 == x2:
        return None
    if min(x1, x2) <= vertical_x <= max(x1, x2):
        t = (vertical_x - x1) / (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return (vertical_x, intersect_y)
    return None

def merge_close_points(points, threshold=6):
    points = np.array(points)
    if len(points) == 0:
        return np.array([])
    if len(points) == 1:
        return points
    merged_points = []
    while len(points) > 0:
        p = points[0]
        close_points = np.linalg.norm(points - p, axis=1) < threshold
        merged_points.append(np.mean(points[close_points], axis=0))
        points = points[~close_points]
    return np.array(merged_points)

def compute_midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def check_distance_pattern(points, k, ab, tolerance=10):
    points = sorted(points, key=lambda p: p[0])
    for i in range(len(points) - 1):
        for j in range(i + 1, len(points)):
            distance = np.linalg.norm(np.array(points[i]) - np.array(points[j]))
            if any((abs(distance - (k + m * ab)) < tolerance for m in [2, 4])):
                return compute_midpoint(points[i], points[j])
    return None
vertical_lines = all_mid_lines
horizontal_lines = joint_horizontal
positive_slope_lines = joint_oblique_positive
negative_slope_lines = joint_oblique_negtive
adjusted_points = []
K_height_pixel = 1079.92 / (1000 * resolution)
AB_height_pixel = 3239.77 / (1000 * resolution)

def _oblique_intersections(vertical_x):
    intersections_with_positive_slope = []
    intersections_with_negative_slope = []
    for segment in positive_slope_lines:
        inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
        if inter_point:
            intersections_with_positive_slope.append(inter_point)
    for segment in negative_slope_lines:
        inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
        if inter_point:
            intersections_with_negative_slope.append(inter_point)
    return (merge_close_points(intersections_with_positive_slope), merge_close_points(intersections_with_negative_slope))

def _all_midpoint_candidates(merge_positive, merge_negative):
    candidates = []
    for p in merge_positive:
        for n in merge_negative:
            candidates.append(compute_midpoint(p, n))
    return candidates

def _choose_midpoint_neighbor_band(candidates, neighbor_ys, default):
    if not candidates:
        return default
    if not neighbor_ys:
        return default
    best = default
    best_dist = None
    for mid in candidates:
        dist = min((abs(mid[1] - y) for y in neighbor_ys))
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = mid
    return best
for vertical_x, _ in vertical_lines:
    intersections_with_horizontal = []
    merge_positive, merge_negative = _oblique_intersections(vertical_x)
    if len(merge_positive) > 0 and len(merge_negative) > 0:
        midpoint = compute_midpoint(merge_positive[0], merge_negative[0])
        adjusted_points.append(('midpoint', midpoint))
    elif len(merge_positive) > 0:
        point = merge_positive[0]
        adjusted_points.append(('positive_slope', (point[0], point[1] + 0.5 * K_height_pixel)))
    elif len(merge_negative) > 0:
        point = merge_negative[0]
        adjusted_points.append(('negative_slope', (point[0], point[1] - 0.5 * K_height_pixel)))
    else:
        for segment in horizontal_lines:
            inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
            if inter_point:
                intersections_with_horizontal.append(inter_point)
        merge_horizontal = merge_close_points(intersections_with_horizontal)
        pattern_midpoint = check_distance_pattern(merge_horizontal, K_height_pixel, AB_height_pixel, tolerance=50)
        if pattern_midpoint:
            adjusted_points.append(('horizontal', pattern_midpoint))
        else:
            if (os.environ.get('PROXY4TUN_ASSUME_FALLBACK') or '1').strip() == '0':
                continue
            assumed_y = None
            if adjusted_points:
                last_point_y = adjusted_points[-1][1][1]
                if 1035 <= last_point_y <= 1265:
                    assumed_y = last_point_y + 431.87
                elif 1422 <= last_point_y <= 1738:
                    assumed_y = last_point_y - 431.87
                elif len(adjusted_points) > 1:
                    second_last_point_y = adjusted_points[-2][1][1]
                    if 1035 <= second_last_point_y <= 1265:
                        assumed_y = second_last_point_y
                    elif 1422 <= second_last_point_y <= 1738:
                        assumed_y = second_last_point_y
                    else:
                        assumed_y = None
                else:
                    assumed_y = None
            else:
                ring_idx = len(adjusted_points)
                assumed_y = 1123.0 if ring_idx % 2 == 0 else 1553.0
            if assumed_y is None:
                ring_idx = len(adjusted_points)
                assumed_y = 1123.0 if ring_idx % 2 == 0 else 1553.0
            adjusted_points.append(('assume', (vertical_x, assumed_y)))
_pairing_mode = (os.environ.get('PROXY4TUN_PAIRING_MODE') or '').strip()
if _pairing_mode in ('neighbor_band', 'neighbor_band_propagate', 'median_slope_band'):
    baseline = list(adjusted_points)
    slope_ys = [coord[1] for label, coord in baseline if label in ('positive_slope', 'negative_slope')]
    slope_median = float(np.median(slope_ys)) if slope_ys else None
    rebuilt = []
    for idx, (label, coord) in enumerate(baseline):
        if label != 'midpoint':
            rebuilt.append((label, coord))
            continue
        vertical_x = coord[0]
        merge_positive, merge_negative = _oblique_intersections(vertical_x)
        candidates = _all_midpoint_candidates(merge_positive, merge_negative)
        if _pairing_mode == 'median_slope_band':
            bands = [slope_median] if slope_median is not None else []
            chosen = _choose_midpoint_neighbor_band(candidates, bands, coord)
        else:
            neighbor_ys = []
            for j in (idx - 1, idx + 1):
                if j < 0 or j >= len(baseline):
                    continue
                if _pairing_mode == 'neighbor_band_propagate' and j < idx:
                    source = rebuilt
                    src_idx = j
                else:
                    source = baseline
                    src_idx = j
                if source[src_idx][0] != 'assume':
                    neighbor_ys.append(source[src_idx][1][1])
            chosen = _choose_midpoint_neighbor_band(candidates, neighbor_ys, coord)
        rebuilt.append(('midpoint', chosen))
    adjusted_points = rebuilt
    extra = ''
    if _pairing_mode == 'median_slope_band':
        extra = f'; slope_median_Y={slope_median}'
    print(f'{_pairing_mode}: midpoint candidates re-scored; band prior applied where available{extra}')
if (os.environ.get('PROXY4TUN_ASSUME_REPAIR') or '').strip() == 'farthest_nonassume_band':
    baseline = list(adjusted_points)
    nonassume_ys = [coord[1] for label, coord in baseline if label in ('positive_slope', 'negative_slope', 'midpoint', 'horizontal')]
    repaired = []
    n_repaired = 0
    for idx, (label, coord) in enumerate(baseline):
        if label != 'assume' or not nonassume_ys:
            repaired.append((label, coord))
            continue
        left = baseline[idx - 1] if idx > 0 else None
        right = baseline[idx + 1] if idx + 1 < len(baseline) else None
        if left is None or right is None or left[0] != 'assume' or (right[0] != 'assume'):
            repaired.append((label, coord))
            continue
        neighbor_mean = 0.5 * (left[1][1] + right[1][1])
        chosen_y = max(nonassume_ys, key=lambda y: abs(y - neighbor_mean))
        repaired.append(('assume', (coord[0], chosen_y)))
        n_repaired += 1
    adjusted_points = repaired
    print(f'assume_repair=farthest_nonassume_band: repaired {n_repaired} sandwiched assume rings using {len(nonassume_ys)} non-assume Y values')
_slope_repair = (os.environ.get('PROXY4TUN_SLOPE_REPAIR') or '').strip()
_do_horizontal = _slope_repair in ('horizontal_if_pattern', 'horizontal_then_other_median', 'horizontal_then_lone_nonassume', 'horizontal_then_other_median_then_lone')
_do_other_median = _slope_repair in ('other_slope_median', 'horizontal_then_other_median', 'horizontal_then_other_median_then_lone')
_do_lone_nonassume = _slope_repair in ('lone_slope_to_nonassume', 'horizontal_then_lone_nonassume', 'horizontal_then_other_median_then_lone')
if _do_horizontal:
    baseline = list(adjusted_points)
    repaired = []
    n_repaired = 0
    for label, coord in baseline:
        if label not in ('positive_slope', 'negative_slope'):
            repaired.append((label, coord))
            continue
        vertical_x = coord[0]
        intersections_with_horizontal = []
        for segment in horizontal_lines:
            inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
            if inter_point:
                intersections_with_horizontal.append(inter_point)
        merge_horizontal = merge_close_points(intersections_with_horizontal)
        pattern_midpoint = check_distance_pattern(merge_horizontal, K_height_pixel, AB_height_pixel, tolerance=50)
        if pattern_midpoint:
            repaired.append(('horizontal', pattern_midpoint))
            n_repaired += 1
        else:
            repaired.append((label, coord))
    adjusted_points = repaired
    print(f'slope_repair=horizontal_if_pattern: replaced {n_repaired} slope rings with horizontal pattern midpoints')
if _do_other_median:
    baseline = list(adjusted_points)
    slope_idxs = [i for i, (label, _) in enumerate(baseline) if label in ('positive_slope', 'negative_slope')]
    repaired = list(baseline)
    n_repaired = 0
    threshold_px = 600.0
    if len(slope_idxs) >= 2:
        for i in slope_idxs:
            label, coord = baseline[i]
            other_ys = [baseline[j][1][1] for j in slope_idxs if j != i]
            other_median = float(np.median(other_ys))
            if abs(coord[1] - other_median) > threshold_px:
                repaired[i] = (label, (coord[0], other_median))
                n_repaired += 1
    adjusted_points = repaired
    print(f'slope_repair=other_slope_median: repaired {n_repaired} slope rings (threshold_px={threshold_px})')
if _do_lone_nonassume:
    baseline = list(adjusted_points)
    slope_idxs = [i for i, (label, _) in enumerate(baseline) if label in ('positive_slope', 'negative_slope')]
    repaired = list(baseline)
    n_repaired = 0
    if len(slope_idxs) == 1:
        i = slope_idxs[0]
        label, coord = baseline[i]
        nonassume_ys = [c[1] for lab, c in baseline if lab in ('midpoint', 'horizontal')]
        if nonassume_ys:
            left = baseline[i - 1] if i > 0 else None
            right = baseline[i + 1] if i + 1 < len(baseline) else None
            if left is not None and right is not None:
                neighbor_mean = 0.5 * (left[1][1] + right[1][1])
                chosen_y = max(nonassume_ys, key=lambda y: abs(y - neighbor_mean))
            else:
                chosen_y = float(np.median(nonassume_ys))
            repaired[i] = ('midpoint', (coord[0], chosen_y))
            n_repaired = 1
    adjusted_points = repaired
    print(f'slope_repair=lone_slope_to_nonassume: repaired {n_repaired} lone slope rings using non-assume Y band')
df_loc = pd.DataFrame(adjusted_points, columns=['Type', 'Coordinates'])
df_loc['X'] = df_loc['Coordinates'].apply(lambda coord: coord[0])
df_loc['Y'] = df_loc['Coordinates'].apply(lambda coord: coord[1])
df_loc = df_loc.drop(columns=['Coordinates'])
df_loc = df_loc.sort_values(by='X').reset_index(drop=True)
print(f'Number of vertical lines: {len(vertical_lines)}')
print(f'Number of adjusted points: {len(adjusted_points)}')
print('DataFrame:')
print(df_loc)
plt.figure(figsize=(16, 16))
ax = plt.gca()
colors = {'horizontal': 'b', 'positive_slope': 'r', 'negative_slope': 'c', 'midpoint': 'm', 'assume': 'g'}
markers = {'horizontal': 'o', 'positive_slope': '^', 'negative_slope': 's', 'midpoint': '*', 'assume': 'd'}
for label, (x, y) in adjusted_points:
    ax.plot(x, y, color=colors[label], marker=markers[label], markersize=10, label=label)
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='lower right')
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_title('Intersection Points')
ax.set_aspect('equal', adjustable='box')
ax.invert_yaxis()
x_min, x_max = (df_loc['X'].min(), df_loc['X'].max())
y_min, y_max = (df_loc['Y'].min(), df_loc['Y'].max())
margin = 0.1
if len(df_loc) > 0:
    x_range = x_max - x_min
    y_range = y_max - y_min
    ax.set_xlim(x_min - margin * x_range, x_max + margin * x_range)
    ax.set_ylim(y_max + margin * y_range, y_min - margin * y_range)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(paths['initial_points']), 'initial_prompt_points.png'), dpi=150, bbox_inches='tight')
df_loc.to_csv(paths['initial_points'], index=False)
import numpy as np
df_loc.to_csv(paths['initial_points'], index=False)
state['df_loc'] = df_loc
save_state(paths['state'], state)
print(f"Detection complete -> {paths['initial_points']}")
