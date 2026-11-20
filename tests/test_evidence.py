from dataclasses import asdict, replace
import json
import unittest

from rsi4tun.evidence import ArtifactBundle, BoundaryArtifact, ComparisonPolicy, DepthArtifact, FULL_STAGES, KArtifact, assert_fixed_evidence, bundle_from_dict, compare_reference, policy_from_dict


def fixture(bundle_id="reference"):
    return ArtifactBundle(
        bundle_id=bundle_id,
        case_id=bundle_id,
        backend="synthetic",
        code_commit="fixture-code",
        artifact_digests=(("depth", "d"), ("boundaries", "b"), ("k", "k"), ("final_3d", "f")),
        completed_stages=FULL_STAGES,
        design_schema="one-key-two-boundaries-v1",
        expected_boundaries_per_ring=2,
        representation_id="canonical-turns-v1",
        registration_id=bundle_id + "-registration",
        registration_audited=True,
        depth=DepthArtifact(((1.0, 1.0, 1.0, 1.0),), ((True, True, True, True),), ((True, True, True, True),), 0.1, 0.1),
        boundaries=BoundaryArtifact(((0.0, 0.5), (0.0, 0.5)), ((0.0, 0.5), (0.0, 0.5)), 10.0, "boundary-detector-v1", "raw-depth-edge-v1"),
        k=KArtifact((0.1, 0.6), (0.1, 0.6), (0.0, 0.0), 1.5, True),
        source_role="expert_reference" if bundle_id == "reference" else "experiment",
        expert_review_id="synthetic-review" if bundle_id == "reference" else None,
    )


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.reference = fixture()
        self.observed = fixture("observed")
        self.policy = ComparisonPolicy(0.02, (self.reference.design_schema,))

    def compare(self, observed):
        return compare_reference(self.reference, observed, self.policy)

    def test_structural_void_is_not_a_depth_hole(self):
        depth = DepthArtifact(((1.0, None, 1.0, 1.0),), ((True, False, True, True),), ((True, False, True, True),), 0.1, 0.1)
        report = self.compare(replace(self.observed, depth=depth))
        self.assertEqual(report.status, "comparable")
        self.assertEqual(report.measurements["depth_valid_coverage"], 1.0)
        self.assertEqual(report.measurements["depth_largest_hole_fraction"], 0.0)
        self.assertNotIn("depth_expected_area_m2__delta", report.features)

    def test_periodic_seam_connects_depth_holes(self):
        depth = DepthArtifact(((None, 1.0, 1.0, None),), ((False, True, True, False),), ((True, True, True, True),), 0.1, 0.1)
        periodic = self.compare(replace(self.observed, depth=depth))
        nonperiodic = self.compare(replace(self.observed, depth=replace(depth, periodic_columns=False)))
        self.assertEqual(periodic.measurements["depth_largest_hole_fraction"], 0.5)
        self.assertEqual(nonperiodic.measurements["depth_largest_hole_fraction"], 0.25)

    def test_false_boundary_and_missing_boundary_have_separate_penalties(self):
        extra = replace(self.observed.boundaries, detected_turns=((0.0, 0.25, 0.5), (0.0, 0.25, 0.5)))
        missed = replace(self.observed.boundaries, detected_turns=((0.0,), (0.0,)))
        extra_report = self.compare(replace(self.observed, boundaries=extra))
        missed_report = self.compare(replace(self.observed, boundaries=missed))
        self.assertAlmostEqual(extra_report.measurements["boundary_support_precision"], 2 / 3)
        self.assertEqual(extra_report.measurements["boundary_support_recall"], 1.0)
        self.assertEqual(missed_report.measurements["boundary_support_precision"], 1.0)
        self.assertEqual(missed_report.measurements["boundary_support_recall"], 0.5)

    def test_boundary_distance_uses_periodic_geometry(self):
        boundaries = replace(self.observed.boundaries, detected_turns=((0.999, 0.499), (0.999, 0.499)))
        report = self.compare(replace(self.observed, boundaries=boundaries))
        self.assertAlmostEqual(report.measurements["boundary_symmetric_distance_fraction"], 0.001)
        self.assertEqual(report.measurements["boundary_support_precision"], 1.0)

    def test_new_design_is_coverage_gap_not_bad_quality(self):
        observed = replace(self.observed, design_schema="five-key-v1", expected_boundaries_per_ring=6)
        report = self.compare(observed)
        self.assertEqual(report.status, "coverage_gap")
        self.assertEqual(report.features, {})
        self.assertTrue(report.measurements)
        self.assertIn("design_coverage_gap", report.reasons)

    def test_unknown_k_identity_abstains_from_k_features(self):
        observed = replace(self.observed, k=replace(self.observed.k, identity_known=False))
        report = self.compare(observed)
        self.assertEqual(report.status, "partial")
        self.assertFalse(any(key.startswith("k_") for key in report.features))
        self.assertIn("k_identity_unknown", report.reasons)

    def test_staggered_design_does_not_create_spurious_k_error(self):
        report = self.compare(self.observed)
        self.assertEqual(report.measurements["k_phase_spread_turns"], 0.0)
        self.assertEqual(report.measurements["k_phase_rms_turns"], 0.0)

    def test_consistent_but_wrong_k_phase_remains_visible(self):
        observed = replace(self.observed, k=replace(self.observed.k, azimuth_turns=(0.2, 0.7)))
        report = self.compare(observed)
        self.assertAlmostEqual(report.measurements["k_phase_spread_turns"], 0.0)
        self.assertAlmostEqual(report.measurements["k_phase_rms_turns"], 0.1)

    def test_empty_support_does_not_become_perfect_agreement(self):
        boundaries = replace(self.observed.boundaries, support_turns=((), ()))
        report = self.compare(replace(self.observed, boundaries=boundaries))
        self.assertEqual(report.status, "invalid")
        self.assertEqual(report.features, {})
        self.assertEqual(report.measurements["depth_valid_coverage"], 1.0)
        self.assertEqual(report.provenance["component_status"]["observed"]["boundaries"], "invalid:empty_boundary_evidence")

    def test_nonfinite_depth_is_invalid(self):
        depth = replace(self.observed.depth, values=((1.0, float("nan"), 1.0, 1.0),))
        report = self.compare(replace(self.observed, depth=depth))
        self.assertEqual(report.status, "invalid")
        self.assertEqual(report.features, {})
        self.assertNotIn("depth_valid_coverage", report.measurements)
        self.assertIn("boundary_support_precision", report.measurements)

    def test_self_referential_edge_support_is_invalid(self):
        boundaries = replace(self.observed.boundaries, support_extractor_id=self.observed.boundaries.detector_id)
        report = self.compare(replace(self.observed, boundaries=boundaries))
        self.assertEqual(report.status, "invalid")

    def test_incomplete_pipeline_cannot_produce_comparison_features(self):
        report = self.compare(replace(self.observed, completed_stages=FULL_STAGES[:-1]))
        self.assertEqual(report.status, "invalid")
        self.assertEqual(report.features, {})
        self.assertEqual(report.measurements, {})

    def test_registration_must_be_audited(self):
        report = self.compare(replace(self.observed, registration_audited=False))
        self.assertEqual(report.status, "coverage_gap")
        self.assertEqual(report.features, {})

    def test_reference_comparison_is_not_pixel_matching(self):
        depth = DepthArtifact(((3.0, 3.0), (3.0, 3.0)), ((True, True), (True, True)), ((True, True), (True, True)), 0.2, 0.2)
        report = self.compare(replace(self.observed, depth=depth))
        self.assertEqual(report.status, "comparable")
        self.assertEqual(report.features["depth_valid_coverage__delta"], 0.0)
        self.assertNotEqual(report.measurements["depth_expected_area_m2"], report.reference_measurements["depth_expected_area_m2"])

    def test_bundle_digest_changes_with_observation(self):
        first = self.compare(self.observed)
        changed = replace(self.observed, k=replace(self.observed.k, axial_offsets_m=(0.0, 0.1)))
        second = self.compare(changed)
        self.assertNotEqual(first.provenance["observed_bundle_digest"], second.provenance["observed_bundle_digest"])

    def test_unreviewed_output_cannot_be_called_expert_reference(self):
        reference = replace(self.reference, expert_review_id=None)
        report = compare_reference(reference, self.observed, self.policy)
        self.assertEqual(report.status, "insufficient_reference")
        self.assertEqual(report.features, {})

    def test_json_round_trip_preserves_contracts(self):
        bundle = bundle_from_dict(json.loads(json.dumps(asdict(self.reference))))
        policy = policy_from_dict(json.loads(json.dumps(asdict(self.policy))))
        self.assertEqual(bundle, self.reference)
        self.assertEqual(policy, self.policy)

    def test_intervention_cannot_remove_expected_depth_support(self):
        depth = replace(self.observed.depth, expected_support=((False, True, True, True),))
        with self.assertRaisesRegex(ValueError, "depth.expected_support"):
            assert_fixed_evidence(self.observed, replace(self.observed, depth=depth))

    def test_intervention_cannot_move_expected_k_target(self):
        k = replace(self.observed.k, expected_azimuth_turns=(0.2, 0.7))
        with self.assertRaisesRegex(ValueError, "k.expected_azimuth_turns"):
            assert_fixed_evidence(self.observed, replace(self.observed, k=k))

    def test_intervention_cannot_redefine_independent_edge_support(self):
        boundaries = replace(self.observed.boundaries, support_turns=((0.25, 0.75), (0.25, 0.75)))
        with self.assertRaisesRegex(ValueError, "boundaries.support_turns"):
            assert_fixed_evidence(self.observed, replace(self.observed, boundaries=boundaries))

    def test_intervention_can_change_outputs_under_fixed_evidence(self):
        boundaries = replace(self.observed.boundaries, detected_turns=((0.01, 0.51), (0.01, 0.51)))
        k = replace(self.observed.k, azimuth_turns=(0.2, 0.7))
        assert_fixed_evidence(self.observed, replace(self.observed, boundaries=boundaries, k=k, code_commit="new-code"))


if __name__ == "__main__":
    unittest.main()
