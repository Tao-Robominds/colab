#!/usr/bin/env python3
                                                                   
                                                                                    
import sys
import os
import matplotlib
matplotlib.use("Agg")

import json

_SAM4TUN_DIR = os.path.dirname(os.path.abspath(__file__))
_SAM_PKG = os.path.join(_SAM4TUN_DIR, "segment-anything")
for _p in (_SAM4TUN_DIR, _SAM_PKG):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from helpers.pipeline_io import ensure_dir
from helpers.pipeline_state import load_state, save_state

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

tunnel_id = sys.argv[1]


from helpers import family_io
from helpers import prompt_placement

params, param_file, family_mode = family_io.load_stage_params("detecting")
print(f"[case=continuous] stage=detecting")

expected_keys = [
    "binary_threshold", "morphological_kernel_size", "dilation_iterations",
    "hough_threshold_oblique", "minLineLength_oblique", "maxLineGap_oblique",
    "hough_threshold_horizontal", "minLineLength_horizontal", "maxLineGap_horizontal",
    "hough_threshold_vertical", "angle_range_oblique_positive", "angle_range_oblique_negative",
    "merge_distance", "ring_spacing_constant", "resolution",
]
for key in expected_keys:
    if key not in params:
        sys.exit(f"Missing required parameter '{key}' in {param_file}")
binary_threshold = params["binary_threshold"]
morphological_kernel_size = params["morphological_kernel_size"]
dilation_iterations = params["dilation_iterations"]
hough_threshold_oblique = params["hough_threshold_oblique"]
minLineLength_oblique = params["minLineLength_oblique"]
maxLineGap_oblique = params["maxLineGap_oblique"]
hough_threshold_horizontal = params["hough_threshold_horizontal"]
minLineLength_horizontal = params["minLineLength_horizontal"]
maxLineGap_horizontal = params["maxLineGap_horizontal"]
hough_threshold_vertical = params["hough_threshold_vertical"]
angle_range_oblique_positive = params["angle_range_oblique_positive"]
angle_range_oblique_negative = params["angle_range_oblique_negative"]
merge_distance = params["merge_distance"]
ring_spacing_constant = params["ring_spacing_constant"]
resolution = params["resolution"]
K_height = float(params.get("K_height", 1079.92))
AB_height = float(params.get("AB_height", 3239.77))
pattern_tolerance = float(params.get("pattern_tolerance", 50))
vertical_rho_mode = params.get("vertical_rho_mode", "max")
vertical_rho_spacing_mm = float(params.get("vertical_rho_spacing_mm", 1200))
vertical_rho_min_factor = float(params.get("vertical_rho_min_factor", 0.0))
vertical_rho_max_factor = float(params.get("vertical_rho_max_factor", 5.0))
                                                                        
                                                                   
prompt_extrapolate_px = int(params.get("prompt_extrapolate_px", 0))
key_pair_max_sep_px = float(params.get("key_pair_max_sep_px", 2609))
_k_row_raw = params.get("k_row_pattern", [1123.0, 1553.0])
k_row_pattern = [float(v) for v in _k_row_raw]
k_row_tolerance = float(params.get("k_row_tolerance", 200.0))
k_row_action = str(params.get("k_row_action", "snap")).lower()
if k_row_action not in ("snap", "fail", "warn"):
    sys.exit(f"Invalid k_row_action={k_row_action!r}; expected snap|fail|warn")
print(f"[case=continuous] detecting")

paths = ensure_dir(tunnel_id)
state = load_state(paths["state"])
df_point_cloud = state["df_point_cloud"]
df_enhance_segment = state["df_enhance_segment"]
df_enhance_joint = state["df_enhance_joint"]
ring_count = state["ring_count"]
depth_map_outlier = state["depth_map_outlier"]

        
binary_map = np.where(np.isnan(depth_map_outlier), 0, 255).astype(np.uint8)

ret, binary_image = cv2.threshold(binary_map, binary_threshold, 255, cv2.THRESH_BINARY)

kernel = np.ones(morphological_kernel_size, np.uint8)

dilated_edges = cv2.dilate(binary_image, kernel, iterations=dilation_iterations)

        
import cv2
import numpy as np
import matplotlib.pyplot as plt

                          
L, W = binary_map.shape

                                           
lines_oblique = cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, hough_threshold_oblique, minLineLength=minLineLength_oblique, maxLineGap=maxLineGap_oblique)

                                                  
lines_horizontal = cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, hough_threshold_horizontal, minLineLength=minLineLength_horizontal, maxLineGap=maxLineGap_horizontal)

                         
lines_vertical = cv2.HoughLines(dilated_edges, 1, np.pi / 180, hough_threshold_vertical)
if lines_vertical is not None:
    rho = lines_vertical[:, 0, 0]
    scale = vertical_rho_spacing_mm / (resolution * 1000)
    if vertical_rho_mode == "w2_offset_band":
                                                                     
        lo = W / 2 + vertical_rho_min_factor * scale
        hi = W / 2 + vertical_rho_max_factor * scale
        filtered = lines_vertical[(rho >= lo) & (rho <= hi)]
        print(f"Vertical rho W/2-offset band [{lo:.1f}, {hi:.1f}] -> {len(filtered)} lines")
        if len(filtered) == 0:
            print("Band empty on this span; keeping unfiltered vertical Hough lines")
        else:
            lines_vertical = filtered
    elif vertical_rho_mode == "band":
        lo = vertical_rho_min_factor * scale
        hi = vertical_rho_max_factor * scale
        filtered = lines_vertical[(rho >= lo) & (rho <= hi)]
        print(f"Vertical rho band filter [{lo:.1f}, {hi:.1f}] -> {len(filtered)} lines")
        if len(filtered) == 0:
            print("Band empty on this span; keeping unfiltered vertical Hough lines")
        else:
            lines_vertical = filtered
    else:
        lines_vertical = lines_vertical[rho <= (vertical_rho_max_factor * scale)]

                      
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

        if angle_range_oblique_positive[0] <= angle <= angle_range_oblique_positive[1]:
            joint_oblique_positive.append(line)
            cv2.line(output_image, (x1, y1), (x2, y2), color_angle1, line_thickness)

        elif angle_range_oblique_negative[0] <= angle <= angle_range_oblique_negative[1]:
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
threshold_distance = merge_distance          

if lines_vertical is not None:
    lines_vertical = lines_vertical[:, 0]                       

                                              
    for i, (rho1, theta1) in enumerate(lines_vertical):
        if -0.5 * np.pi / 180 <= abs(theta1) <= 0.5 * np.pi / 180:                                
            x1, y1 = rho1 * np.cos(theta1), rho1 * np.sin(theta1)
            is_merged = False
            
                                                     
            for j, (rho2, theta2) in enumerate(merged_lines):
                x2, y2 = rho2 * np.cos(theta2), rho2 * np.sin(theta2)
                if np.sqrt((x1 - x2)**2 + (y1 - y2)**2) < threshold_distance:
                                 
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
        x1 = int(x0 + 2677 * (-b))
        y1 = int(y0 + 2677 * (a))
        x2 = int(x0 - 2677 * (-b))
        y2 = int(y0 - 2677 * (a))
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
        x1 = int(x0 + L * (-b))
        y1 = int(y0 + L * (a))
        x2 = int(x0 - L * (-b))
        y2 = int(y0 - L * (a))
        cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)

                                                       
    distances = []
    for i in range(len(mid_lines) - 1):
        rho1, theta1 = mid_lines[i]
        rho2, theta2 = mid_lines[i + 1]
        x1, y1 = rho1 * np.cos(theta1), rho1 * np.sin(theta1)
        x2, y2 = rho2 * np.cos(theta2), rho2 * np.sin(theta2)
        distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        distances.append(distance)

    avg_distance_detected = np.mean(distances) if distances else 0
    
    avg_distance_designed = W/ring_count
    
                                                                                       
    if bool(params.get("prefer_designed_spacing", False)):
        avg_distance = avg_distance_designed
    elif np.abs(avg_distance_detected - (ring_spacing_constant / resolution)) <= np.abs(avg_distance_designed - (ring_spacing_constant / resolution)):
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
            x1 = int(x0 + L * (-b))
            y1 = int(y0 + L * (a))
            x2 = int(x0 - L * (-b))
            y2 = int(y0 - L * (a))
            cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)
            all_mid_lines.append((x0, leftmost_theta))                                 
            x0 -= avg_distance
    
                                 
        rightmost_rho, rightmost_theta = mid_lines[-1]
        a = np.cos(rightmost_theta)
        b = np.sin(rightmost_theta)
        x0 = a * rightmost_rho
        y0 = b * rightmost_rho
    
                                          
        while x0 <= output_image.shape[1]:
            x1 = int(x0 + L * (-b))
            y1 = int(y0 + L * (a))
            x2 = int(x0 - L * (-b))
            y2 = int(y0 - L * (a))
            cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)
            all_mid_lines.append((x0, rightmost_theta))                                 
            x0 += avg_distance

    all_mid_lines = sorted(list(set(all_mid_lines)), key=lambda line: line[0])

                                                                           
_n_vertical_hough = 0 if lines_vertical is None else int(len(lines_vertical))
_vertical_fallback = False
if lines_vertical is None or len(all_mid_lines) == 0:
    _vertical_fallback = True
    print("No vertical lines detected. Using fallback method: Creating evenly spaced vertical lines based on ring count.")
    all_mid_lines = []
    
                                                                               
    block_width = W / ring_count

    for i in range(ring_count):
                                                   
        x_pos = (i + 0.5) * block_width
                                                                                    
                                                          
        all_mid_lines.append((x_pos, 0))
        
                                                                      
        x1, y1 = int(x_pos), 0
        x2, y2 = int(x_pos), L
        cv2.line(output_image, (x1, y1), (x2, y2), color_mid_lines, line_thickness)

    print(f"Generated {len(all_mid_lines)} synthetic vertical lines at ring centers")

print(
    f"[dd_counts] n_oblique_pos={len(joint_oblique_positive)} "
    f"n_oblique_neg={len(joint_oblique_negtive)} "
    f"n_horizontal={len(joint_horizontal)} "
    f"n_vertical={_n_vertical_hough} "
    f"vertical_fallback={int(_vertical_fallback)}"
)

                    
plt.figure(figsize=(12, 12))
plt.imshow(output_image)
plt.savefig(paths["detected_lines"], dpi=150, bbox_inches='tight')

def line_segment_vertical_intersection(vertical_x, segment, extrapolate_px=0):

    x1, y1, x2, y2 = segment
    if x1 == x2:
        return None
    pad = max(0, int(extrapolate_px))
    if min(x1, x2) - pad <= vertical_x <= max(x1, x2) + pad:
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
            if any(abs(distance - (k + m * ab)) < tolerance for m in [2, 4]):
                return compute_midpoint(points[i], points[j])
    return None

vertical_lines = all_mid_lines
horizontal_lines = joint_horizontal
positive_slope_lines = joint_oblique_positive
negative_slope_lines = joint_oblique_negtive
adjusted_points = []
K_height_pixel = K_height / (1000 * resolution)
AB_height_pixel = AB_height / (1000 * resolution)

adjusted_points = prompt_placement.place_prompts_carrying_previous_ring(
    vertical_lines,
    positive_slope_lines,
    negative_slope_lines,
    horizontal_lines,
    K_height_pixel,
    AB_height_pixel,
    pattern_tolerance,
    L,
    line_segment_vertical_intersection,
    merge_close_points,
    compute_midpoint,
    check_distance_pattern,
)
adjusted_points, k_row_gate_record = prompt_placement.snap_k_centres_to_design_row(
    adjusted_points,
    k_row_pattern,
    k_row_tolerance,
    k_row_action,
    paths,
)

df_loc = pd.DataFrame(adjusted_points, columns=['Type', 'Coordinates'])
df_loc['X'] = df_loc['Coordinates'].apply(lambda coord: coord[0])
df_loc['Y'] = df_loc['Coordinates'].apply(lambda coord: coord[1])
df_loc = df_loc.drop(columns=['Coordinates'])
df_loc = df_loc.sort_values(by='X').reset_index(drop=True)

print(f"Number of vertical lines: {len(vertical_lines)}")
print(f"Number of adjusted points: {len(adjusted_points)}")
print(df_loc)

plt.figure(figsize=(16, 16))
ax = plt.gca()
colors = {'horizontal': 'b', 'positive_slope': 'r', 'negative_slope': 'c', 'midpoint': 'm', 'assume': 'g', 'propagated': 'y'}
markers = {'horizontal': 'o', 'positive_slope': '^', 'negative_slope': 's', 'midpoint': '*', 'assume': 'd', 'propagated': 'P'}
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
if len(df_loc) > 0:
    x_min, x_max = df_loc['X'].min(), df_loc['X'].max()
    y_min, y_max = df_loc['Y'].min(), df_loc['Y'].max()
    margin = 0.1
    x_range = x_max - x_min
    y_range = y_max - y_min
    ax.set_xlim(x_min - margin * x_range, x_max + margin * x_range)
    ax.set_ylim(y_max + margin * y_range, y_min - margin * y_range)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(paths["initial_points"]), "initial_prompt_points.png"), dpi=150, bbox_inches='tight')

df_loc.to_csv(paths["initial_points"], index=False)
state["df_loc"] = df_loc
save_state(paths["state"], state)
if k_row_gate_record is not None:
    _gate_path = os.path.join(os.path.dirname(paths["initial_points"]), "k_row_gate.json")
    with open(_gate_path, "w") as _gf:
        json.dump(k_row_gate_record, _gf, indent=2)
        _gf.write("\n")
    print(f"K-row gate evidence -> {_gate_path}")
print(f"Detection complete -> {paths['initial_points']}")

