import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from rsi4tun.adapters import run_synthetic
from rsi4tun.contracts import canonical, file_digest, read_json


class RunIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.output = Path(self.temporary.name) / "run"
        self.run = run_synthetic(
            {"case_id": "fixture-case", "scan_id": "fixture-scan"},
            {"missing_columns": 3, "phase_correction_turns": 0.0},
            self.output,
            "a" * 40,
            "b" * 40,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def mutate_bundle(self, mutation):
        path = Path(self.run.artifact_path)
        bundle = read_json(path)
        mutation(bundle)
        path.write_bytes(canonical(bundle) + b"\n")
        return replace(self.run, artifact_sha256=file_digest(path))

    def mutate_stage(self, stage_name, mutation):
        path = self.output / "stages" / (stage_name + ".json")
        data = read_json(path)
        mutation(data)
        path.write_bytes(canonical(data) + b"\n")
        hashes = tuple((name, file_digest(path) if name == stage_name else value) for name, value in self.run.stage_digests)
        return replace(self.run, stage_digests=hashes)

    def test_complete_fixture_and_stage_chain_pass(self):
        self.run.require_complete()
        previous = None
        for stage_name, stage_digest in self.run.stage_digests:
            stage = read_json(self.output / "stages" / (stage_name + ".json"))
            self.assertEqual(stage["input_stage_digest"], previous)
            previous = stage_digest

    def test_rehashed_bundle_cannot_replace_recorded_depth(self):
        changed = self.mutate_bundle(lambda bundle: bundle["depth"]["values"][0].__setitem__(3, 200.0))
        with self.assertRaisesRegex(ValueError, "depth_stage_data_mismatch"):
            changed.require_complete()

    def test_rehashed_bundle_cannot_replace_geometry(self):
        for field, key in (("boundaries", "circumference_m"), ("k", "ring_pitch_m")):
            with self.subTest(field=field):
                path = Path(self.run.artifact_path)
                original = path.read_bytes()
                changed = self.mutate_bundle(lambda bundle: bundle[field].__setitem__(key, 50.0))
                with self.assertRaisesRegex(ValueError, "stage_data_mismatch"):
                    changed.require_complete()
                path.write_bytes(original)

    def test_changed_prediction_vector_is_not_the_recorded_output(self):
        labels = tuple((value + 1) % 4 for value in self.run.predicted_labels)
        with self.assertRaisesRegex(ValueError, "final_labels_stage_mismatch"):
            replace(self.run, predicted_labels=labels).require_complete()

    def test_configuration_must_be_consistent_across_stages(self):
        changed = self.mutate_stage("enhancement", lambda stage: stage.__setitem__("configuration_digest", "c" * 64))
        with self.assertRaisesRegex(ValueError, "stage_configuration_mismatch"):
            changed.require_complete()

    def test_stage_chain_cannot_be_rebound(self):
        changed = self.mutate_stage("enhancement", lambda stage: stage.__setitem__("input_stage_digest", "d" * 64))
        with self.assertRaisesRegex(ValueError, "stage_chain_mismatch"):
            changed.require_complete()

    def test_stage_revision_must_match_completed_run(self):
        changed = self.mutate_stage("enhancement", lambda stage: stage.__setitem__("code_commit", "c" * 40))
        with self.assertRaisesRegex(ValueError, "stage_run_provenance_mismatch"):
            changed.require_complete()

    def test_named_digest_must_resolve_to_the_correct_stage(self):
        changed = self.mutate_bundle(lambda bundle: bundle["artifact_digests"][0].__setitem__(1, "d" * 64))
        with self.assertRaisesRegex(ValueError, "named_artifact_stage_mismatch"):
            changed.require_complete()


if __name__ == "__main__":
    unittest.main()
