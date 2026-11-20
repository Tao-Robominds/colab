from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence


def _encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_encoded(value)).hexdigest()


def _file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            result.update(chunk)
    return result.hexdigest()


def _write_once(path: Path, value: object) -> None:
    data = _encoded(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError("ARCHIVE_COLLISION") from None


@dataclass(frozen=True)
class Revision:
    commit: str
    tree: str
    bundle_path: str
    bundle_sha256: str
    required_paths: tuple[str, ...]
    external_assets: tuple[tuple[str, str], ...]

    @property
    def manifest_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class ExecutionReceipt:
    revision_commit: str
    revision_tree: str
    revision_manifest_digest: str
    command: tuple[str, ...]
    returncode: int
    stdout_path: str
    stdout_sha256: str
    stderr_path: str
    stderr_sha256: str
    output_dir: str
    output_artifacts: tuple[tuple[str, str], ...]
    worktree_clean: bool
    registration_path: str | None = None
    registration_digest: str | None = None

    @property
    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class EvaluationReceipt:
    experiment_id: str
    run_id: str
    revision_commit: str
    revision_tree: str
    execution_digest: str
    proxy_digest: str
    evidence_digest: str
    gate_passed: bool
    accepted_baseline_commit: str | None

    @property
    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class ReleaseReceipt:
    commit: str
    tree: str
    revision_manifest_digest: str
    evaluation_digest: str
    execution_digest: str
    previous_commit: str | None
    previous_release_oid: str | None

    @property
    def digest(self) -> str:
        return _digest(asdict(self))


class CodeStore:
    accepted_ref = "refs/rsi/accepted"
    release_ref = "refs/rsi/current-release"

    def __init__(self, repo: Path, archive: Path):
        self.repo = Path(repo).resolve()
        self.archive = Path(archive).resolve()
        if self.archive == self.repo or self.repo in self.archive.parents:
            raise ValueError("ARCHIVE_MUST_BE_OUTSIDE_REPOSITORY")
        top = self._git("rev-parse", "--show-toplevel").decode().strip()
        if Path(top).resolve() != self.repo:
            raise ValueError("REPOSITORY_ROOT_REQUIRED")
        self.archive.mkdir(parents=True, exist_ok=True)

    def _git(self, *args: str, input_data: bytes | None = None, cwd: Path | None = None) -> bytes:
        result = subprocess.run(
            ("git", "-c", "core.hooksPath=/dev/null", *args),
            cwd=cwd or self.repo,
            input=input_data,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise ValueError("GIT_COMMAND_FAILED:" + result.stderr.decode(errors="replace").strip())
        return result.stdout

    def _read_ref(self, name: str) -> str | None:
        result = subprocess.run(
            ("git", "rev-parse", "--verify", "--quiet", name),
            cwd=self.repo,
            capture_output=True,
            check=False,
        )
        if result.returncode == 1:
            return None
        if result.returncode:
            raise ValueError("INVALID_GIT_REF")
        return result.stdout.decode().strip()

    def accepted_commit(self) -> str | None:
        return self._read_ref(self.accepted_ref)

    def _require_clean(self, root: Path, required_paths: Sequence[str]) -> None:
        if self._git("status", "--porcelain=v1", "--untracked-files=all", cwd=root).strip():
            raise ValueError("DIRTY_CODE_TREE")
        ignored = self._git("ls-files", "--others", "--ignored", "--exclude-standard", "-z", cwd=root)
        allowed_ignored = (Path("venv"), Path("sam4tun") / "segment-anything")
        for raw in ignored.split(b"\0"):
            if not raw:
                continue
            relative = Path(os.fsdecode(raw))
            if any(relative == prefix or prefix in relative.parents for prefix in allowed_ignored):
                continue
            if "__pycache__" in relative.parts and relative.suffix in (".pyc", ".pyo"):
                continue
            source_suffixes = {".py", ".sh", ".bash", ".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h", ".rs", ".go", ".ipynb", ".so", ".pyd", ".dll"}
            if relative.suffix in source_suffixes or any(relative == Path(entry) or Path(entry) in relative.parents for entry in required_paths):
                raise ValueError("IGNORED_REQUIRED_SOURCE")
        entries = self._git("ls-files", "--stage", "-z", cwd=root)
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            mode = entry.split(b" ", 1)[0]
            if mode == b"160000":
                raise ValueError("SUBMODULE_NOT_BUNDLED")
            if mode == b"120000":
                raise ValueError("SYMLINK_NOT_BUNDLED")

    def freeze(
        self,
        required_paths: Sequence[str] = ("src", "configs", "pyproject.toml", "environment.lock.json"),
        external_assets: Mapping[str, str] | None = None,
    ) -> Revision:
        required = tuple(required_paths)
        for entry in required:
            candidate = Path(entry)
            if candidate.is_absolute() or ".." in candidate.parts or not entry:
                raise ValueError("INVALID_REQUIRED_SOURCE_PATH")
        self._require_clean(self.repo, required)
        commit = self._git("rev-parse", "HEAD").decode().strip()
        tree = self._git("rev-parse", commit + "^{tree}").decode().strip()
        tracked = tuple(os.fsdecode(item) for item in self._git("ls-tree", "-r", "--name-only", "-z", commit).split(b"\0") if item)
        for entry in required:
            if not any(path == entry or path.startswith(entry.rstrip("/") + "/") for path in tracked):
                raise ValueError("MISSING_REQUIRED_SOURCE:" + entry)
        assets = tuple(sorted((external_assets or {}).items()))
        for name, checksum in assets:
            if not name or len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
                raise ValueError("INVALID_EXTERNAL_ASSET_DIGEST")
        bundle = self.archive / "bundles" / (commit + ".bundle")
        bundle.parent.mkdir(parents=True, exist_ok=True)
        if not bundle.exists():
            pending = bundle.with_suffix(".pending")
            self._git("bundle", "create", str(pending), "HEAD")
            self._git("bundle", "verify", str(pending))
            os.replace(pending, bundle)
        self._git("bundle", "verify", str(bundle))
        revision = Revision(commit, tree, str(bundle), _file_digest(bundle), required, assets)
        _write_once(self.archive / "revisions" / (revision.manifest_digest + ".json"), asdict(revision))
        self.verify_revision(revision)
        return revision

    def verify_revision(self, revision: Revision) -> None:
        saved = self.archive / "revisions" / (revision.manifest_digest + ".json")
        if not saved.is_file() or saved.read_bytes() != _encoded(asdict(revision)):
            raise ValueError("UNKNOWN_REVISION")
        bundle = Path(revision.bundle_path)
        if not bundle.is_file() or _file_digest(bundle) != revision.bundle_sha256:
            raise ValueError("BUNDLE_DIGEST_MISMATCH")
        tree = self._git("rev-parse", revision.commit + "^{tree}").decode().strip()
        if tree != revision.tree:
            raise ValueError("REVISION_TREE_MISMATCH")
        heads = self._git("bundle", "list-heads", str(bundle)).decode().splitlines()
        if not any(line.split()[0] == revision.commit for line in heads):
            raise ValueError("BUNDLE_REVISION_MISMATCH")

    def assert_unchanged(self, baseline: Revision, candidate: Revision, protected_paths: Sequence[str]) -> None:
        self.verify_revision(baseline)
        self.verify_revision(candidate)
        paths = tuple(protected_paths)
        for entry in paths:
            if not entry or Path(entry).is_absolute() or ".." in Path(entry).parts:
                raise ValueError("INVALID_PROTECTED_PATH")
        changed = self._git("diff", "--name-only", "-z", baseline.commit, candidate.commit)
        for raw in changed.split(b"\0"):
            if not raw:
                continue
            name = os.fsdecode(raw)
            if any(name == entry or name.startswith(entry.rstrip("/") + "/") for entry in paths):
                raise ValueError("PROTECTED_CODE_CHANGED:" + name)

    def read_revision_file(self, revision: Revision, relative_path: str) -> bytes:
        self.verify_revision(revision)
        path = Path(relative_path)
        if not relative_path or path.is_absolute() or ".." in path.parts:
            raise ValueError("INVALID_REVISION_FILE_PATH")
        return self._git("show", revision.commit + ":" + path.as_posix())

    def execute(
        self,
        revision: Revision,
        command: Sequence[str],
        output_dir: Path,
        timeout: float = 300.0,
        environment: Mapping[str, str] | None = None,
        registration: tuple[Path, str] | None = None,
    ) -> ExecutionReceipt:
        self.verify_revision(revision)
        if registration is not None:
            if _digest(json.loads(registration[0].read_text())) != registration[1]:
                raise ValueError("REGISTRATION_INTEGRITY_FAILURE")
        if not command or not all(isinstance(argument, str) and argument for argument in command):
            raise ValueError("INVALID_EXECUTION_COMMAND")
        output = Path(output_dir).resolve()
        if output == self.repo or self.repo in output.parents:
            raise ValueError("OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")
        output.mkdir(parents=True, exist_ok=False)
        parent = Path(tempfile.mkdtemp(prefix="rsi4tun-version-"))
        checkout = parent / "checkout"
        self._git("worktree", "add", "--detach", str(checkout), revision.commit)
        run_environment = os.environ.copy()
        run_environment.update(environment or {})
        run_environment.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "RSI_CODE_COMMIT": revision.commit,
            "RSI_CODE_TREE": revision.tree,
            "RSI_REVISION_DIGEST": revision.manifest_digest,
            "RSI_OUTPUT_DIR": str(output),
        })
        if registration is not None:
            run_environment["RSI_REGISTRATION_DIGEST"] = registration[1]
        previous_pythonpath = run_environment.get("PYTHONPATH", "")
        run_environment["PYTHONPATH"] = str(checkout / "src") + (os.pathsep + previous_pythonpath if previous_pythonpath else "")
        stdout_path = output / "stdout.bin"
        stderr_path = output / "stderr.bin"
        clean = False
        returncode = -1
        try:
            self._require_clean(checkout, revision.required_paths)
            with stdout_path.open("xb") as stdout_stream, stderr_path.open("xb") as stderr_stream:
                try:
                    result = subprocess.run(
                        tuple(command),
                        cwd=checkout,
                        env=run_environment,
                        stdout=stdout_stream,
                        stderr=stderr_stream,
                        timeout=timeout,
                        check=False,
                    )
                    returncode = result.returncode
                except subprocess.TimeoutExpired:
                    returncode = -124
            try:
                self._require_clean(checkout, revision.required_paths)
                clean = True
            except ValueError:
                clean = False
            if self._git("rev-parse", "HEAD", cwd=checkout).decode().strip() != revision.commit:
                clean = False
            output_artifacts = []
            for path in sorted(output.rglob("*")):
                if path.is_symlink():
                    raise ValueError("SYMLINK_OUTPUT_ARTIFACT")
                if path.is_file() and path not in (stdout_path, stderr_path):
                    output_artifacts.append((path.relative_to(output).as_posix(), _file_digest(path)))
            receipt = ExecutionReceipt(
                revision.commit,
                revision.tree,
                revision.manifest_digest,
                tuple(command),
                returncode,
                str(stdout_path),
                _file_digest(stdout_path),
                str(stderr_path),
                _file_digest(stderr_path),
                str(output),
                tuple(output_artifacts),
                clean,
                str(registration[0]) if registration else None,
                registration[1] if registration else None,
            )
            if registration is not None and _digest(json.loads(registration[0].read_text())) != registration[1]:
                raise ValueError("REGISTRATION_CHANGED_DURING_EXECUTION")
            _write_once(self.archive / "executions" / (receipt.digest + ".json"), asdict(receipt))
            return receipt
        finally:
            self._git("worktree", "remove", "--force", str(checkout))
            shutil.rmtree(parent)

    def _verify_execution(self, revision: Revision, execution_digest: str) -> ExecutionReceipt:
        path = self.archive / "executions" / (execution_digest + ".json")
        if not path.is_file():
            raise ValueError("UNKNOWN_EXECUTION")
        payload = json.loads(path.read_text())
        payload["command"] = tuple(payload["command"])
        payload["output_artifacts"] = tuple(tuple(item) for item in payload["output_artifacts"])
        receipt = ExecutionReceipt(**payload)
        if receipt.digest != execution_digest:
            raise ValueError("EXECUTION_RECEIPT_MISMATCH")
        if (receipt.revision_commit, receipt.revision_tree, receipt.revision_manifest_digest) != (
            revision.commit, revision.tree, revision.manifest_digest
        ):
            raise ValueError("EXECUTION_REVISION_MISMATCH")
        if receipt.returncode != 0 or receipt.worktree_clean is not True:
            raise ValueError("UNACCEPTABLE_EXECUTION")
        if receipt.registration_digest is not None:
            if not receipt.registration_path or _digest(json.loads(Path(receipt.registration_path).read_text())) != receipt.registration_digest:
                raise ValueError("REGISTRATION_INTEGRITY_FAILURE")
        for filename, checksum in ((receipt.stdout_path, receipt.stdout_sha256), (receipt.stderr_path, receipt.stderr_sha256)):
            artifact = Path(filename)
            if not artifact.is_file() or _file_digest(artifact) != checksum:
                raise ValueError("EXECUTION_ARTIFACT_CHANGED")
        for relative, checksum in receipt.output_artifacts:
            artifact = Path(receipt.output_dir) / relative
            if not artifact.is_file() or artifact.is_symlink() or _file_digest(artifact) != checksum:
                raise ValueError("EXECUTION_ARTIFACT_CHANGED")
        return receipt

    def verify_execution(self, revision: Revision, execution_digest: str) -> ExecutionReceipt:
        self.verify_revision(revision)
        return self._verify_execution(revision, execution_digest)

    def promote(self, revision: Revision, evaluation: EvaluationReceipt) -> ReleaseReceipt:
        self.verify_revision(revision)
        if evaluation.gate_passed is not True:
            raise ValueError("GATE_DID_NOT_PASS")
        if (evaluation.revision_commit, evaluation.revision_tree) != (revision.commit, revision.tree):
            raise ValueError("EVALUATION_REVISION_MISMATCH")
        if not evaluation.experiment_id or not evaluation.run_id:
            raise ValueError("MISSING_EVALUATION_ID")
        for checksum in (evaluation.execution_digest, evaluation.proxy_digest, evaluation.evidence_digest):
            if len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
                raise ValueError("INVALID_EVALUATION_DIGEST")
        self._verify_execution(revision, evaluation.execution_digest)
        previous = self.accepted_commit()
        if previous != evaluation.accepted_baseline_commit:
            raise ValueError("ACCEPTED_BASELINE_CHANGED")
        previous_release = self._read_ref(self.release_ref)
        release = ReleaseReceipt(
            revision.commit, revision.tree, revision.manifest_digest,
            evaluation.digest, evaluation.execution_digest, previous, previous_release,
        )
        _write_once(self.archive / "evaluations" / (evaluation.digest + ".json"), asdict(evaluation))
        _write_once(self.archive / "releases" / (release.digest + ".json"), asdict(release))
        blob = self._git("hash-object", "-w", "--stdin", input_data=_encoded(asdict(release))).decode().strip()
        zero = "0" * len(revision.commit)
        transaction = "\n".join((
            "start",
            "create refs/rsi/releases/" + release.digest + " " + blob,
            "update " + self.accepted_ref + " " + revision.commit + " " + (previous or zero),
            "update " + self.release_ref + " " + blob + " " + (previous_release or zero),
            "prepare",
            "commit",
            "",
        ))
        self._git("update-ref", "--stdin", input_data=transaction.encode())
        return release

    def restore(self, release: ReleaseReceipt) -> str:
        saved = self.archive / "releases" / (release.digest + ".json")
        if not saved.is_file() or saved.read_bytes() != _encoded(asdict(release)):
            raise ValueError("UNKNOWN_RELEASE")
        if release.previous_commit is None or release.previous_release_oid is None:
            raise ValueError("NO_PREVIOUS_RELEASE")
        current_blob = self._read_ref("refs/rsi/releases/" + release.digest)
        if current_blob is None or self._read_ref(self.release_ref) != current_blob:
            raise ValueError("RELEASE_IS_NOT_CURRENT")
        transaction = "\n".join((
            "start",
            "update " + self.accepted_ref + " " + release.previous_commit + " " + release.commit,
            "update " + self.release_ref + " " + release.previous_release_oid + " " + current_blob,
            "prepare",
            "commit",
            "",
        ))
        self._git("update-ref", "--stdin", input_data=transaction.encode())
        return release.previous_commit
