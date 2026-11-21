from __future__ import annotations

import json
import os
import sys

import numpy as np


def place_prompts_carrying_previous_ring(
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
):
    adjusted_points = []
    for vertical_x, _ in vertical_lines:
        intersections_with_positive_slope = []
        intersections_with_negative_slope = []
        intersections_with_horizontal = []
        for segment in positive_slope_lines:
            inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
            if inter_point:
                intersections_with_positive_slope.append(inter_point)
        for segment in negative_slope_lines:
            inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
            if inter_point:
                intersections_with_negative_slope.append(inter_point)
        merge_positive = merge_close_points(intersections_with_positive_slope)
        merge_negative = merge_close_points(intersections_with_negative_slope)
        current_type = None
        current_y = None
        if len(merge_positive) > 0 and len(merge_negative) > 0:
            midpoint = compute_midpoint(merge_positive[0], merge_negative[0])
            current_y = midpoint[1]
            current_type = "midpoint"
        elif len(merge_positive) > 0:
            point = merge_positive[0]
            current_y = point[1] - 0.5 * K_height_pixel
            current_type = "positive_slope"
        elif len(merge_negative) > 0:
            point = merge_negative[0]
            current_y = point[1] + 0.5 * K_height_pixel
            current_type = "negative_slope"
        else:
            for segment in horizontal_lines:
                inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
                if inter_point:
                    intersections_with_horizontal.append(inter_point)
            merge_horizontal = merge_close_points(intersections_with_horizontal)
            if len(merge_horizontal) > 0:
                min_y = min(merge_horizontal, key=lambda x: x[1])[1]
                max_y = max(merge_horizontal, key=lambda x: x[1])[1]
                current_y = (min_y + max_y) / 2
                current_type = "horizontal"
            elif adjusted_points:
                current_y = adjusted_points[-1][1][1]
                current_type = "assume"
            else:
                current_y = L * 0.5
                current_type = "assume"
                print(f"Warning: no starting detection at x={vertical_x}; using image mid Y")
        if adjusted_points and current_type != "assume":
            last_point_y = adjusted_points[-1][1][1]
            if abs(current_y - last_point_y) / max(abs(last_point_y), 1e-6) > 0.1:
                current_y = last_point_y
                current_type = "assume"
        adjusted_points.append((current_type, (vertical_x, current_y)))
    return adjusted_points


def snap_k_centres_to_design_row(adjusted_points, k_row_pattern, k_row_tolerance, k_row_action, paths):
    anchor_types = {"midpoint", "horizontal", "positive_slope", "negative_slope"}
    anchor_ys = [pt[1] for label, pt in adjusted_points if label in anchor_types]
    if not anchor_ys:
        return adjusted_points, None
    y_star_measured = float(np.median(anchor_ys))
    if len(anchor_ys) > 1 and np.std(anchor_ys) > 40:
        print(f"Warning: anchor Y std {np.std(anchor_ys):.1f} > 40 before design-row snap")
    nearest_row = float(min(k_row_pattern, key=lambda r: abs(r - y_star_measured)))
    distance = float(abs(y_star_measured - nearest_row))
    within = distance <= k_row_tolerance
    y_star_used = y_star_measured
    action_taken = "accept"
    if within:
        print(
            f"K-row gate OK: y_star={y_star_measured:.1f} within "
            f"{distance:.1f}px of design row {nearest_row:.1f} "
            f"(tol={k_row_tolerance:.1f})"
        )
    else:
        msg = (
            f"K-row gate TRIGGERED: y_star={y_star_measured:.1f} is "
            f"{distance:.1f}px from nearest design row {nearest_row:.1f} "
            f"(tol={k_row_tolerance:.1f}, action={k_row_action})"
        )
        if k_row_action == "fail":
            print(msg)
            print("Aborting stage 4 so the runner can retry with another seed. Exit code 3.")
            gate_dir = os.path.dirname(paths["initial_points"])
            os.makedirs(gate_dir, exist_ok=True)
            with open(os.path.join(gate_dir, "k_row_gate.json"), "w") as gf:
                json.dump(
                    {
                        "y_star_measured": y_star_measured,
                        "y_star_used": None,
                        "nearest_design_row": nearest_row,
                        "distance_px": distance,
                        "tolerance_px": k_row_tolerance,
                        "k_row_pattern": k_row_pattern,
                        "within_tolerance": False,
                        "action_requested": k_row_action,
                        "action_taken": "fail",
                        "n_anchor_ys": len(anchor_ys),
                        "anchor_y_std": float(np.std(anchor_ys)) if len(anchor_ys) > 1 else 0.0,
                    },
                    gf,
                    indent=2,
                )
                gf.write("\n")
            raise SystemExit(3)
        if k_row_action == "snap":
            y_star_used = nearest_row
            action_taken = "snap"
            print(msg)
            print(f"K-row gate SNAP: replacing y_star with {y_star_used:.1f}")
        else:
            action_taken = "warn"
            print(f"WARNING: {msg} — proceeding with measured y_star")
    count = len(adjusted_points)
    adjusted_points = [("propagated", (pt[0], y_star_used)) for _, pt in adjusted_points]
    print(f"K uniform: set all {count} rings to Y={y_star_used:.1f}")
    record = {
        "y_star_measured": y_star_measured,
        "y_star_used": y_star_used,
        "nearest_design_row": nearest_row,
        "distance_px": distance,
        "tolerance_px": k_row_tolerance,
        "k_row_pattern": k_row_pattern,
        "within_tolerance": within,
        "action_requested": k_row_action,
        "action_taken": action_taken,
        "n_anchor_ys": len(anchor_ys),
        "anchor_y_std": float(np.std(anchor_ys)) if len(anchor_ys) > 1 else 0.0,
    }
    return adjusted_points, record
