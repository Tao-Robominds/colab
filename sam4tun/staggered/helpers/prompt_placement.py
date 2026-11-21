from __future__ import annotations

def place_prompts_on_alternating_rows(
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
        if len(merge_positive) > 0 and len(merge_negative) > 0:
            midpoint = compute_midpoint(merge_positive[0], merge_negative[0])
            adjusted_points.append(("midpoint", midpoint))
        elif len(merge_positive) > 0:
            point = merge_positive[0]
            adjusted_points.append(("positive_slope", (point[0], point[1] + 0.5 * K_height_pixel)))
        elif len(merge_negative) > 0:
            point = merge_negative[0]
            adjusted_points.append(("negative_slope", (point[0], point[1] - 0.5 * K_height_pixel)))
        else:
            for segment in horizontal_lines:
                inter_point = line_segment_vertical_intersection(vertical_x, segment[0])
                if inter_point:
                    intersections_with_horizontal.append(inter_point)
            merge_horizontal = merge_close_points(intersections_with_horizontal)
            pattern_midpoint = check_distance_pattern(
                merge_horizontal, K_height_pixel, AB_height_pixel, tolerance=pattern_tolerance
            )
            if pattern_midpoint:
                adjusted_points.append(("horizontal", pattern_midpoint))
            else:
                assumed_y = None
                if adjusted_points:
                    last_point_y = adjusted_points[-1][1][1]
                    if 1035 <= last_point_y <= 1265:
                        assumed_y = last_point_y + 431.87
                    elif 1422 <= last_point_y <= 1738:
                        assumed_y = last_point_y - 431.87
                    else:
                        if len(adjusted_points) > 1:
                            second_last_point_y = adjusted_points[-2][1][1]
                            if 1035 <= second_last_point_y <= 1265:
                                assumed_y = second_last_point_y
                            elif 1422 <= second_last_point_y <= 1738:
                                assumed_y = second_last_point_y
                if assumed_y is None:
                    ring_idx = len(adjusted_points)
                    assumed_y = 1123.0 if ring_idx % 2 == 0 else 1553.0
                adjusted_points.append(("assume", (vertical_x, assumed_y)))
    return adjusted_points

