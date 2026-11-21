from statistics import mean

from rsi4tun.proxy import DevelopmentRow, FrozenProxy, fit_proxy

FEATURE_IDS = ("k_wedge", "angle_positive", "ab_rel_error", "proud_cut")
AB_NOMINAL = 3239.77
CONTRACT = "sample-tune-proxy-v1"
BACKEND = "sample_tune"
PROXY_ID = "sample_tune_v1"


def ab_rel_error(ab_height: float) -> float:
    return abs(float(ab_height) - AB_NOMINAL) / AB_NOMINAL


def features(k_wedge: float, angle_positive: float, ab_height: float, proud_cut: float):
    return (
        ("k_wedge", float(k_wedge)),
        ("angle_positive", float(angle_positive)),
        ("ab_rel_error", ab_rel_error(ab_height)),
        ("proud_cut", float(proud_cut)),
    )


def sample_tune_rows() -> tuple[DevelopmentRow, ...]:
    rows = (
        ("pre_tune", 0, 1, AB_NOMINAL, 0, 0.880, True),
        ("t01_oracle_gt", 0, 1, AB_NOMINAL, 0, 0.876, False),
        ("t02_angle_neg", 0, 0, AB_NOMINAL, 0, 0.267, False),
        ("t03_mirror_k", 1, 1, AB_NOMINAL, 0, 0.894, False),
        ("t04_angle_neg_mirror", 1, 0, AB_NOMINAL, 0, 0.286, False),
        ("t05_mirror_angle_8", 1, 1, AB_NOMINAL, 0, 0.894, False),
        ("t06_mirror_angle_7", 1, 1, AB_NOMINAL, 0, 0.892, False),
        ("t07_mirror_kheight", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t08_mirror_detect_swap", 1, 1, AB_NOMINAL, 0, 0.859, False),
        ("t09_kh_1120", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t10_kh_1150", 1, 1, AB_NOMINAL, 0, 0.893, False),
        ("t11_kh_1080", 1, 1, AB_NOMINAL, 0, 0.894, False),
        ("t12_kh1100_ab3300", 1, 1, 3300.0, 0, 0.839, False),
        ("t13_kh1100_width1250", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t14_kh1100_angle7_8", 1, 1, AB_NOMINAL, 0, 0.894, False),
        ("t15_oracle_mirror_kh1120", 1, 1, AB_NOMINAL, 0, 0.890, False),
        ("t16_pad200", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t17_crop30", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t18_taper500", 1, 1, AB_NOMINAL, 0, 0.894, False),
        ("t19_ybounds", 1, 1, AB_NOMINAL, 0, 0.895, False),
        ("t20_ab3200", 1, 1, 3200.0, 0, 0.881, False),
        ("t21_denoise_tight", 1, 1, AB_NOMINAL, 0, 0.845, False),
        ("t22_denoise_mid", 1, 1, AB_NOMINAL, 0, 0.896, False),
        ("t23_enhance_no_outlier", 1, 1, AB_NOMINAL, 0, 0.897, False),
        ("t24_enhance_window3", 1, 1, AB_NOMINAL, 0, 0.892, False),
        ("t25_denoise_offset_p005", 1, 1, AB_NOMINAL, 0, 0.731, False),
        ("t26_template_scale_097", 1, 1, AB_NOMINAL, 0, 0.878, False),
        ("t27_overlap_abstain", 1, 1, AB_NOMINAL, 0, 0.887, False),
        ("t28_margin_abstain", 1, 1, AB_NOMINAL, 0, 0.896, False),
        ("t29_radius_abs_5mm", 1, 1, AB_NOMINAL, 0, 0.899, False),
        ("t30_proud_5mm", 1, 1, AB_NOMINAL, 1, 0.902, False),
    )
    return tuple(
        DevelopmentRow(
            "sample",
            "sample",
            run_id,
            features(k_wedge, angle_positive, ab_height, proud_cut),
            miou,
            is_baseline,
        )
        for run_id, k_wedge, angle_positive, ab_height, proud_cut, miou, is_baseline in rows
    )


def fit_sample_proxy() -> FrozenProxy:
    return fit_proxy(
        sample_tune_rows(),
        FEATURE_IDS,
        proxy_id=PROXY_ID,
        evidence_contract_digest=CONTRACT,
        backend=BACKEND,
    )


def in_sample_mae(proxy: FrozenProxy) -> float:
    rows = sample_tune_rows()
    errors = [
        abs(proxy.predict(dict(row.features), CONTRACT, BACKEND) - row.final_miou)
        for row in rows
    ]
    return float(mean(errors))


def proxy_record(proxy: FrozenProxy | None = None) -> dict:
    fitted = proxy or fit_sample_proxy()
    return {
        "proxy_id": fitted.proxy_id,
        "target": "final_3d_semantic_miou",
        "status": "development_fit_pending",
        "scope": {
            "family": "sample",
            "scan": "data/scans/sample.txt",
            "case_id": "sample",
            "group_id": "sample",
        },
        "feature_ids": list(fitted.feature_ids),
        "centres": list(fitted.centres),
        "scales": list(fitted.scales),
        "weights": list(fitted.weights),
        "intercept": fitted.intercept,
        "evidence_contract_digest": fitted.evidence_contract_digest,
        "backend": fitted.backend,
        "validation_receipt": fitted.validation_receipt,
        "fit_rows_digest": fitted.fit_rows_digest,
        "n_rows": len(sample_tune_rows()),
        "in_sample_mae": in_sample_mae(fitted),
        "equation": "clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)",
        "notes": (
            "Refit after t29 and t30. proud_cut is 1 only on t30. "
            "accepted_wisdom stays empty until a grouped release."
        ),
    }
