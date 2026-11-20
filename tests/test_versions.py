import ast
import io
import json
import subprocess
import sys
import tempfile
import tokenize
import unittest
from dataclasses import replace
from pathlib import Path

from rsi4tun.versions import CodeStore, EvaluationReceipt


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@invalid.example")
        self.git("config", "user.name", "Version fixture")
        (self.repo / "src").mkdir()
        (self.repo / "configs").mkdir()
        (self.repo / "src" / "run.py").write_text("import os\nprint(os.environ['RSI_CODE_COMMIT'])\n")
        (self.repo / "configs" / "policy.json").write_text("{\"threshold\":0.01}\n")
        (self.repo / "pyproject.toml").write_text("[project]\nname = 'fixture'\nversion = '0.0.1'\n")
        (self.repo / "environment.lock.json").write_text("{\"python\":\"3.12\"}\n")
        (self.repo / ".gitignore").write_text("__pycache__/\n*.ignored\n")
        self.commit()
        self.store = CodeStore(self.repo, self.root / "archive")

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args):
        return subprocess.run(("git", *args), cwd=self.repo, check=True, capture_output=True).stdout.decode().strip()

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "fixture")

    def execute(self, revision, name):
        return self.store.execute(revision, (sys.executable, "src/run.py"), self.root / name)

    def evaluation(self, revision, execution, gate=True):
        return EvaluationReceipt(
            "experiment-1", "run-1", revision.commit, revision.tree, execution.digest,
            "a" * 64, "b" * 64, gate, self.store.accepted_commit(),
        )

    def test_full_source_recovers_from_bundle(self):
        revision = self.store.freeze(external_assets={"weights": "c" * 64})
        destination = self.root / "recovered"
        subprocess.run(("git", "clone", "-q", revision.bundle_path, str(destination)), check=True, capture_output=True)
        self.assertEqual((destination / "src" / "run.py").read_bytes(), (self.repo / "src" / "run.py").read_bytes())
        self.assertEqual((destination / "configs" / "policy.json").read_bytes(), (self.repo / "configs" / "policy.json").read_bytes())
        self.assertTrue((destination / "environment.lock.json").is_file())
        self.assertEqual(revision.external_assets, (("weights", "c" * 64),))

    def test_dirty_untracked_and_ignored_required_code_are_rejected(self):
        source = self.repo / "src" / "run.py"
        original = source.read_text()
        source.write_text(original + "print(1)\n")
        with self.assertRaisesRegex(ValueError, "DIRTY_CODE_TREE"):
            self.store.freeze()
        source.write_text(original)
        added = self.repo / "src" / "extra.py"
        added.write_text("value = 1\n")
        with self.assertRaisesRegex(ValueError, "DIRTY_CODE_TREE"):
            self.store.freeze()
        added.unlink()
        hidden = self.repo / "src" / "extra.ignored"
        hidden.write_text("value = 1\n")
        with self.assertRaisesRegex(ValueError, "IGNORED_REQUIRED_SOURCE"):
            self.store.freeze()

    def test_ignored_venv_and_segment_anything_are_allowed(self):
        gitignore = self.repo / ".gitignore"
        gitignore.write_text(gitignore.read_text() + "venv/\nsam4tun/segment-anything/\n")
        self.commit()
        (self.repo / "venv" / "lib").mkdir(parents=True)
        (self.repo / "venv" / "lib" / "site.py").write_text("value = 1\n")
        (self.repo / "sam4tun" / "segment-anything").mkdir(parents=True)
        (self.repo / "sam4tun" / "segment-anything" / "build_sam.py").write_text("value = 1\n")
        revision = self.store.freeze()
        self.assertTrue(revision.commit)

    def test_ignored_source_outside_environment_trees_is_rejected(self):
        gitignore = self.repo / ".gitignore"
        gitignore.write_text(gitignore.read_text() + "venv/\nsam4tun/segment-anything/\ntools/\n")
        self.commit()
        (self.repo / "tools").mkdir()
        (self.repo / "tools" / "helper.py").write_text("value = 1\n")
        with self.assertRaisesRegex(ValueError, "IGNORED_REQUIRED_SOURCE"):
            self.store.freeze()

    def test_tracked_symlink_is_rejected(self):
        (self.repo / "src" / "linked.py").symlink_to("run.py")
        self.commit()
        with self.assertRaisesRegex(ValueError, "SYMLINK_NOT_BUNDLED"):
            self.store.freeze()

    def test_execution_uses_frozen_commit_with_dirty_editor_tree(self):
        revision = self.store.freeze()
        (self.repo / "src" / "run.py").write_text("raise RuntimeError('modified')\n")
        execution = self.execute(revision, "run-frozen")
        self.assertEqual(execution.returncode, 0)
        self.assertTrue(execution.worktree_clean)
        self.assertEqual(Path(execution.stdout_path).read_text().strip(), revision.commit)
        self.assertIn("modified", (self.repo / "src" / "run.py").read_text())

    def test_mutating_execution_cannot_be_promoted(self):
        (self.repo / "src" / "run.py").write_text("from pathlib import Path\nPath('src/run.py').write_text('value = 3\\n')\n")
        self.commit()
        revision = self.store.freeze()
        execution = self.execute(revision, "run-mutating")
        self.assertFalse(execution.worktree_clean)
        with self.assertRaisesRegex(ValueError, "UNACCEPTABLE_EXECUTION"):
            self.store.promote(revision, self.evaluation(revision, execution))
        self.assertIsNone(self.store.accepted_commit())

    def test_gate_revision_artifact_and_baseline_are_verified(self):
        revision = self.store.freeze()
        execution = self.execute(revision, "run-gates")
        evaluation = self.evaluation(revision, execution)
        with self.assertRaisesRegex(ValueError, "GATE_DID_NOT_PASS"):
            self.store.promote(revision, replace(evaluation, gate_passed=False))
        with self.assertRaisesRegex(ValueError, "EVALUATION_REVISION_MISMATCH"):
            self.store.promote(revision, replace(evaluation, revision_commit="0" * 40))
        with self.assertRaisesRegex(ValueError, "UNKNOWN_EXECUTION"):
            self.store.promote(revision, replace(evaluation, execution_digest="c" * 64))
        with self.assertRaisesRegex(ValueError, "ACCEPTED_BASELINE_CHANGED"):
            self.store.promote(revision, replace(evaluation, accepted_baseline_commit="d" * 40))
        Path(execution.stdout_path).write_text("tampered\n")
        with self.assertRaisesRegex(ValueError, "EXECUTION_ARTIFACT_CHANGED"):
            self.store.promote(revision, evaluation)
        self.assertIsNone(self.store.accepted_commit())

    def test_promote_and_restore_change_refs_without_resetting_source(self):
        first = self.store.freeze()
        first_execution = self.execute(first, "first")
        first_release = self.store.promote(first, self.evaluation(first, first_execution))
        self.assertEqual(self.store.accepted_commit(), first.commit)
        (self.repo / "src" / "run.py").write_text("import os\nprint(os.environ['RSI_CODE_COMMIT'])\nprint(2)\n")
        self.commit()
        second = self.store.freeze()
        second_execution = self.execute(second, "second")
        second_release = self.store.promote(second, self.evaluation(second, second_execution))
        self.assertEqual(self.store.accepted_commit(), second.commit)
        self.assertEqual(self.store.restore(second_release), first.commit)
        self.assertEqual(self.store.accepted_commit(), first.commit)
        self.assertEqual(self.git("rev-parse", "HEAD"), second.commit)
        self.assertIn("print(2)", (self.repo / "src" / "run.py").read_text())
        with self.assertRaisesRegex(ValueError, "NO_PREVIOUS_RELEASE"):
            self.store.restore(first_release)

    def test_bundle_tamper_rejected(self):
        revision = self.store.freeze()
        with Path(revision.bundle_path).open("ab") as stream:
            stream.write(b"tampered")
        with self.assertRaisesRegex(ValueError, "BUNDLE_DIGEST_MISMATCH"):
            self.execute(revision, "run-bundle")

    def test_protected_evaluator_paths_cannot_change(self):
        baseline = self.store.freeze()
        (self.repo / "src" / "run.py").write_text("print(3)\n")
        self.commit()
        candidate = self.store.freeze()
        with self.assertRaisesRegex(ValueError, "PROTECTED_CODE_CHANGED"):
            self.store.assert_unchanged(baseline, candidate, ("src",))
        self.store.assert_unchanged(baseline, candidate, ("configs",))

    def test_run_artifact_tamper_prevents_promotion(self):
        (self.repo / "src" / "run.py").write_text("import os\nfrom pathlib import Path\nPath(os.environ['RSI_OUTPUT_DIR'], 'result.json').write_text('{}')\n")
        self.commit()
        revision = self.store.freeze()
        execution = self.execute(revision, "run-artifact")
        self.assertEqual(len(execution.output_artifacts), 1)
        (Path(execution.output_dir) / "result.json").write_text("{\"changed\":true}")
        with self.assertRaisesRegex(ValueError, "EXECUTION_ARTIFACT_CHANGED"):
            self.store.promote(revision, self.evaluation(revision, execution))

    def test_missing_required_source_rejected(self):
        (self.repo / "environment.lock.json").unlink()
        self.commit()
        with self.assertRaisesRegex(ValueError, "MISSING_REQUIRED_SOURCE"):
            self.store.freeze()

    def test_owned_python_contains_no_comments_or_docstrings(self):
        module = Path(__file__).parents[1] / "src" / "rsi4tun" / "versions.py"
        for file in (module, Path(__file__)):
            source = file.read_text()
            self.assertFalse(any(token.type == tokenize.COMMENT for token in tokenize.generate_tokens(io.StringIO(source).readline)))
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    self.assertIsNone(ast.get_docstring(node))


if __name__ == "__main__":
    unittest.main()
