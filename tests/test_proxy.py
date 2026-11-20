from dataclasses import replace
import unittest

from rsi4tun.proxy import DevelopmentRow, FrozenProxy, ValidationPolicy, fit_proxy, release_proxy, validate_proxy


def training_rows():
    rows = []
    for case in ("train-a", "train-b"):
        for index, (x, y) in enumerate(((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0))):
            rows.append(DevelopmentRow(case, case + "-group", case + str(index), (("x", x), ("y", y)), 0.2 + 0.5 * x + 0.3 * y, index == 0))
    return tuple(rows)


def heldout_rows(prefix="held", refit=False):
    rows = []
    points = ((0.8, 0.0), (0.6, 1.0)) if refit else ((0.0, 0.0), (1.0, 0.0))
    for suffix in ("a", "b"):
        case = prefix + suffix
        for index, (x, y) in enumerate(points):
            rows.append(DevelopmentRow(case, case + "-group", case + str(index), (("x", x), ("y", y)), 0.2 + 0.5 * x + 0.3 * y, index == 0))
    return tuple(rows)


class ProxyTests(unittest.TestCase):
    def setUp(self):
        self.training = training_rows()
        self.policy = ValidationPolicy()
        self.initial = self.fit(("x",), "p0")
        receipt = validate_proxy(self.initial, None, self.training, heldout_rows(), ("x",), self.policy)
        self.incumbent = release_proxy(self.initial, receipt)
        self.candidate = self.fit(("x", "y"), "p1")

    def fit(self, keys, name):
        return fit_proxy(self.training, keys, proxy_id=name, evidence_contract_digest="contract-v1", backend="synthetic")

    def validate(self, candidate=None, heldout=None, new_features=("y",)):
        return validate_proxy(candidate or self.candidate, self.incumbent, self.training, heldout or heldout_rows("refit", True), new_features, self.policy)

    def test_fit_remains_unusable_until_release(self):
        with self.assertRaisesRegex(ValueError, "unvalidated_proxy"):
            self.candidate.score({"x": 0.5, "y": 1.0}, "contract-v1", "synthetic")

    def test_grouped_refit_uses_final_miou_and_can_release(self):
        validation = self.validate()
        self.assertEqual(validation.decision, "accept")
        self.assertLess(validation.new_mae, validation.old_mae)
        self.assertGreater(validation.selection_gain, 0.0)
        released = release_proxy(self.candidate, validation)
        self.assertGreater(released.score({"x": 0.6, "y": 1.0}, "contract-v1", "synthetic"), released.score({"x": 0.8, "y": 0.0}, "contract-v1", "synthetic"))

    def test_regression_rejects_and_cannot_release(self):
        heldout = tuple(replace(row, final_miou=0.9 if row.is_baseline else 0.1) for row in heldout_rows("bad", True))
        validation = self.validate(heldout=heldout)
        self.assertEqual(validation.decision, "reject_validation_regression")
        with self.assertRaisesRegex(ValueError, "proxy_release_not_validated"):
            release_proxy(self.candidate, validation)

    def test_training_rows_are_bound_to_fitted_proxy(self):
        changed = tuple(replace(row, final_miou=0.4) for row in self.training)
        with self.assertRaisesRegex(ValueError, "fit_provenance_mismatch"):
            validate_proxy(self.candidate, self.incumbent, changed, heldout_rows("refit", True), ("y",), self.policy)

    def test_duplicate_feature_names_are_not_silently_overwritten(self):
        duplicate = replace(self.training[0], features=(("x", 0.1), ("x", 0.9)))
        with self.assertRaisesRegex(ValueError, "invalid_development_features"):
            fit_proxy((duplicate,) + self.training[1:], ("x",), proxy_id="bad", evidence_contract_digest="contract-v1", backend="synthetic")

    def test_duplicate_run_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_development_run"):
            self.validate(heldout=heldout_rows() + (heldout_rows()[0],))

    def test_case_cannot_belong_to_two_validation_groups(self):
        heldout = heldout_rows()
        changed = (heldout[0], replace(heldout[1], group_id="other")) + heldout[2:]
        with self.assertRaisesRegex(ValueError, "inconsistent_case_group"):
            self.validate(heldout=changed)

    def test_heldout_miou_range_and_finiteness_are_checked(self):
        for value in (1.1, float("nan"), float("inf")):
            with self.subTest(value=value):
                heldout = heldout_rows()
                with self.assertRaises(ValueError):
                    self.validate(heldout=(replace(heldout[0], final_miou=value),) + heldout[1:])

    def test_existing_feature_cannot_be_relabelled_new(self):
        with self.assertRaisesRegex(ValueError, "candidate_feature_already_used"):
            self.validate(new_features=("x", "y"))

    def test_duplicate_new_feature_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing_candidate_features"):
            self.validate(new_features=("y", "y"))

    def test_old_feature_cannot_be_removed(self):
        candidate = self.fit(("y",), "removed-x")
        with self.assertRaisesRegex(ValueError, "incumbent_features_removed"):
            self.validate(candidate=candidate)

    def test_overflow_is_not_clipped_into_a_perfect_score(self):
        proxy = FrozenProxy("overflow", ("x",), (0.0,), (1.0,), (1e308,), 0.0, "contract-v1", "fixture", "synthetic")
        with self.assertRaisesRegex(ValueError, "non_finite_measurement"):
            proxy.score({"x": 1e308}, "contract-v1", "synthetic")

    def test_single_variant_case_cannot_validate_selection(self):
        heldout = tuple(row for row in heldout_rows() if row.is_baseline)
        self.assertEqual(self.validate(heldout=heldout).decision, "insufficient_selection_candidates")

    def test_missing_explicit_baseline_cannot_validate_selection(self):
        heldout = tuple(replace(row, is_baseline=False) for row in heldout_rows())
        self.assertEqual(self.validate(heldout=heldout).decision, "insufficient_selection_candidates")

    def test_initial_proxy_must_beat_training_mean_benchmark(self):
        wrong = replace(self.initial, weights=(-self.initial.weights[0],))
        validation = validate_proxy(wrong, None, self.training, heldout_rows(), ("x",), self.policy)
        self.assertEqual(validation.decision, "reject_validation_regression")

    def test_one_heldout_group_is_insufficient_even_with_good_fit(self):
        heldout = tuple(replace(row, group_id="single") for row in heldout_rows("refit", True))
        self.assertEqual(self.validate(heldout=heldout).decision, "insufficient_coverage")

    def test_refit_checks_incumbent_training_overlap(self):
        heldout = heldout_rows("refit", True)
        incumbent = replace(self.incumbent, fit_case_ids=self.incumbent.fit_case_ids + (heldout[0].case_id,))
        with self.assertRaisesRegex(ValueError, "incumbent_split_leakage"):
            validate_proxy(self.candidate, incumbent, self.training, heldout, ("y",), self.policy)

    def test_validation_receipt_cannot_release_changed_coefficients(self):
        validation = self.validate()
        changed = replace(self.candidate, intercept=self.candidate.intercept + 0.01)
        with self.assertRaisesRegex(ValueError, "proxy_release_not_validated"):
            release_proxy(changed, validation)


if __name__ == "__main__":
    unittest.main()
