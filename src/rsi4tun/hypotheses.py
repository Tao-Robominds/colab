def depth_limits_k(baseline, interventions, parameters):
    width = parameters["interval_half_width"]
    result = {}
    for name, changes in interventions.items():
        depth_change = changes.get("depth_repair_fraction", 0.0)
        phase_change = changes.get("phase_correction_turns", 0.0)
        expected = {
            "depth_valid_coverage__delta": depth_change,
            "k_phase_rms_turns__delta": -parameters["depth_to_k"] * depth_change - parameters["direct_phase_effect"] * phase_change,
        }
        expected["boundary_symmetric_distance_fraction__delta"] = expected["k_phase_rms_turns__delta"] / 4
        result[name] = {key: (value - width, value + width) for key, value in expected.items()}
    return result


def phase_limits_k(baseline, interventions, parameters):
    width = parameters["interval_half_width"]
    result = {}
    for name, changes in interventions.items():
        depth_change = changes.get("depth_repair_fraction", 0.0)
        phase_change = changes.get("phase_correction_turns", 0.0)
        expected = {
            "depth_valid_coverage__delta": depth_change,
            "k_phase_rms_turns__delta": -parameters["incidental_depth_effect"] * depth_change - parameters["phase_to_k"] * phase_change,
        }
        expected["boundary_symmetric_distance_fraction__delta"] = expected["k_phase_rms_turns__delta"] / 4
        result[name] = {key: (value - width, value + width) for key, value in expected.items()}
    return result
