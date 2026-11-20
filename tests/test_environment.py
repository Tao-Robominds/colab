import tempfile
import unittest
from pathlib import Path

from rsi4tun.quality import audit_code


class EnvironmentBoundaryTests(unittest.TestCase):
    def test_audit_skips_vendored_trees_and_rejects_src_comments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            (root / "src" / "clean.py").write_text("value = 1\n")
            (root / "sam4tun").mkdir()
            (root / "sam4tun" / "stage.py").write_text("# vendor comment\nvalue = 1\n")
            (root / "pipeline").mkdir()
            (root / "pipeline" / "stage.py").write_text('"""vendor docstring"""\nvalue = 1\n')
            (root / "venv" / "lib").mkdir(parents=True)
            (root / "venv" / "lib" / "site.py").write_text("# venv comment\nvalue = 1\n")
            result = audit_code(root)
            self.assertTrue(result["passed"])
            self.assertEqual(result["checked_files"], 1)
            (root / "src" / "dirty.py").write_text("# project comment\nvalue = 1\n")
            dirty = audit_code(root)
            self.assertFalse(dirty["passed"])
            self.assertTrue(any(item[2] == "comment" for item in dirty["violations"]))

    def test_scans_live_once_under_data_scans_with_six_fields(self):
        root = Path(__file__).resolve().parents[1]
        names = ("sample.txt", "1-1.txt", "3-1.txt", "5-1.txt")
        for name in names:
            scan = root / "data" / "scans" / name
            self.assertTrue(scan.is_file(), name)
            with scan.open() as stream:
                fields = len(stream.readline().split())
            self.assertEqual(fields, 6, name)
        self.assertTrue((root / "data" / "deployment").is_dir())
        self.assertFalse(any((root / "data" / "deployment").rglob("*.txt")))
        self.assertFalse((root / "data" / "development" / "scans").exists())


if __name__ == "__main__":
    unittest.main()
