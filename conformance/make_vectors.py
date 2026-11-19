# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate conformance/vectors from the signed example bundle.

    uv run --script conformance/make_vectors.py

Inputs: examples/mock-bundle/ (an extracted, signed bundle produced by the reference CLI; see
examples/README.md) and examples/mock-bundle.pub. Each invalid vector applies one targeted
mutation. "Consistent forgeries" also rebuild the statement and MANIFEST.json, so only the
rule under test fails, which is what someone without the signing key can always do.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import shutil
import tarfile
from collections.abc import Callable
from pathlib import Path

SPEC_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = SPEC_ROOT / "examples" / "mock-bundle"
PUBKEY = SPEC_ROOT / "examples" / "mock-bundle.pub"
OUT = SPEC_ROOT / "conformance" / "vectors"
EVIDENCE, STATEMENT, MANIFEST, SIGNATURE = (
    "evidence.json",
    "attestation.intoto.json",
    "MANIFEST.json",
    "MANIFEST.json.minisig",
)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def rebuild_statement(bundle: Path) -> None:
    """Re-derive the predicate copies and evidence digests from evidence.json."""
    evidence = load(bundle / EVIDENCE)
    statement = load(bundle / STATEMENT)
    predicate = statement["predicate"]
    predicate["agent"] = evidence["subject"]["agent"]
    predicate["configuration"] = evidence["subject"]["configuration"]
    predicate["summary"] = evidence["summary"]
    predicate["limitations"] = evidence["limitations"]
    for document in predicate["evidence_documents"]:
        if (bundle / document["path"]).is_file():
            document["digest"] = digest(bundle / document["path"])
    dump(bundle / STATEMENT, statement)


def rebuild_manifest(bundle: Path, drop_signature: bool = True) -> None:
    files = sorted(
        p.relative_to(bundle).as_posix()
        for p in bundle.rglob("*")
        if p.is_file() and p.name not in (MANIFEST, SIGNATURE)
    )
    dump(
        bundle / MANIFEST,
        {"manifest_version": 1, "files": [{"path": f, "sha256": digest(bundle / f)} for f in files]},
    )
    if drop_signature:
        (bundle / SIGNATURE).unlink(missing_ok=True)


def edit_evidence(fn: Callable[[dict], None]) -> Callable[[Path], None]:
    """Mutate evidence.json, then forge a consistent statement and manifest."""

    def apply(bundle: Path) -> None:
        evidence = load(bundle / EVIDENCE)
        fn(evidence)
        dump(bundle / EVIDENCE, evidence)
        rebuild_statement(bundle)
        rebuild_manifest(bundle)

    return apply


def edit_statement(fn: Callable[[dict], None]) -> Callable[[Path], None]:
    def apply(bundle: Path) -> None:
        statement = load(bundle / STATEMENT)
        fn(statement)
        dump(bundle / STATEMENT, statement)
        rebuild_manifest(bundle)

    return apply


def drop_limitation(code: str) -> Callable[[dict], None]:
    def fn(evidence: dict) -> None:
        evidence["limitations"] = [l for l in evidence["limitations"] if l["code"] != code]

    return fn


def fold_not_tested_in_summary(evidence: dict) -> None:
    evidence["summary"]["passed"] += evidence["summary"]["not_tested"]
    evidence["summary"]["not_tested"] = 0


def undercount_critical(evidence: dict) -> None:
    evidence["summary"]["critical_failures"] = 0


def judge_without_config(evidence: dict) -> None:
    evidence["cases"][0]["assertions"][0]["evaluator_class"] = "llm_judge"
    evidence["cases"][0]["critical"] = False
    for assertion in evidence["cases"][0]["assertions"]:
        assertion.pop("critical", None)
    evidence["summary"]["critical_failures"] = sum(
        1
        for c in evidence["cases"]
        if c["critical"] and c["status"] in ("failed", "error", "timed_out", "flaky")
    )
    evidence["subject"]["configuration"].pop("judge", None)


def judge_only_unlisted(evidence: dict) -> None:
    case = next(c for c in evidence["cases"] if c["critical"] and c["assertions"])
    for assertion in case["assertions"]:
        assertion["evaluator_class"] = "llm_judge"
    evidence["subject"]["configuration"]["judge"] = {"model": "example-judge", "temperature": 0.2}


def duplicate_case(evidence: dict) -> None:
    evidence["cases"].append(copy.deepcopy(evidence["cases"][0]))
    first = evidence["cases"][0]
    evidence["summary"]["total"] += 1
    evidence["summary"][first["status"]] += 1
    evidence["subject"]["configuration"]["test_suite"]["case_count"] += 1
    if first["critical"] and first["status"] in ("failed", "error", "timed_out", "flaky"):
        evidence["summary"]["critical_failures"] += 1


def invalid_status(evidence: dict) -> None:
    evidence["cases"][0]["status"] = "skipped"


def wrong_subject_digest(statement: dict) -> None:
    statement["subject"][0]["digest"]["sha256"] = "0" * 64


def predicate_summary_differs(statement: dict) -> None:
    statement["predicate"]["summary"]["failed"] = 0


def references_manifest(statement: dict) -> None:
    statement["predicate"]["evidence_documents"].append(
        {"path": MANIFEST, "digest": "sha256:" + "0" * 64}
    )


def tamper_without_manifest(bundle: Path) -> None:
    report = bundle / "report.md"
    report.write_text(report.read_text() + "\nAll cases passed.\n")


def add_unlisted_file(bundle: Path) -> None:
    (bundle / "extra.txt").write_text("not in the manifest\n")


def remove_statement(bundle: Path) -> None:
    (bundle / STATEMENT).unlink()
    rebuild_manifest(bundle)


def resign_attempt(bundle: Path) -> None:
    """Edit evidence and fix the manifest, but keep the old signature."""
    evidence = load(bundle / EVIDENCE)
    fold_not_tested_in_summary(evidence)
    dump(bundle / EVIDENCE, evidence)
    rebuild_statement(bundle)
    rebuild_manifest(bundle, drop_signature=False)


VECTORS: list[tuple[str, str, Callable[[Path], None] | None, dict]] = [
    ("valid", "signed-mock-bundle", None,
     {"result": "verified", "pubkey": "test.pub", "description": "The example bundle, signed."}),
    ("valid", "unsigned-mock-bundle", lambda b: (b / SIGNATURE).unlink(),
     {"result": "integrity_only", "description": "The example bundle without its signature."}),
    ("invalid", "sem-001-not-tested-folded-into-passed", edit_evidence(fold_not_tested_in_summary),
     {"result": "nonconformant", "rules": ["SEM-001"],
      "description": "Summary reports the not-tested case as passed (INV-1)."}),
    ("invalid", "sem-002-critical-failures-undercounted", edit_evidence(undercount_critical),
     {"result": "nonconformant", "rules": ["SEM-002"],
      "description": "A failed critical case is missing from critical_failures (INV-2)."}),
    ("invalid", "sem-003-unobserved-tool-calls-unlabelled",
     edit_evidence(drop_limitation("tool_calls_not_observed")),
     {"result": "nonconformant", "rules": ["SEM-003"],
      "description": "Synthesized tool calls without the tool_calls_not_observed limitation (INV-3)."}),
    ("invalid", "sem-004-judge-only-critical-unlisted", edit_evidence(judge_only_unlisted),
     {"result": "nonconformant", "rules": ["SEM-004"],
      "description": "A critical case decided only by an LLM judge is not disclosed (INV-4)."}),
    ("invalid", "sem-005-mock-unlabelled", edit_evidence(drop_limitation("mock_execution")),
     {"result": "nonconformant", "rules": ["SEM-005"],
      "description": "Mock execution without the mock_execution limitation."}),
    ("invalid", "sem-006-partial-suite-unlabelled", edit_evidence(drop_limitation("partial_suite")),
     {"result": "nonconformant", "rules": ["SEM-006"],
      "description": "Not-tested cases without the partial_suite limitation (INV-1)."}),
    ("invalid", "sem-007-judge-without-configuration", edit_evidence(judge_without_config),
     {"result": "nonconformant", "rules": ["SEM-007"],
      "description": "llm_judge assertions with no recorded judge configuration (INV-4)."}),
    ("invalid", "sem-008-duplicate-case-id", edit_evidence(duplicate_case),
     {"result": "nonconformant", "rules": ["SEM-008"],
      "description": "The same case id appears twice."}),
    ("invalid", "sch-001-invalid-status", edit_evidence(invalid_status),
     {"result": "nonconformant", "rules": ["SCH-001"],
      "description": "A case status outside the schema enum."}),
    ("invalid", "xdoc-001-manifest-in-predicate", edit_statement(references_manifest),
     {"result": "nonconformant", "rules": ["XDOC-001"],
      "description": "The predicate references MANIFEST.json (circular digest)."}),
    ("invalid", "xdoc-002-predicate-summary-differs", edit_statement(predicate_summary_differs),
     {"result": "nonconformant", "rules": ["XDOC-002"],
      "description": "The statement summary disagrees with evidence.json."}),
    ("invalid", "xdoc-003-wrong-subject-digest", edit_statement(wrong_subject_digest),
     {"result": "nonconformant", "rules": ["XDOC-003"],
      "description": "A statement subject digest does not match the tested artifact."}),
    ("invalid", "bnd-003-unlisted-file", add_unlisted_file,
     {"result": "failed", "rules": ["BND-003"], "description": "A file not listed in the manifest."}),
    ("invalid", "bnd-004-tampered-file", tamper_without_manifest,
     {"result": "failed", "rules": ["BND-004"], "description": "report.md edited after export."}),
    ("invalid", "bnd-005-missing-statement", remove_statement,
     {"result": "nonconformant", "rules": ["BND-005"],
      "description": "evidence.json without attestation.intoto.json."}),
    ("invalid", "sig-001-forged-after-signing", resign_attempt,
     {"result": "failed", "rules": ["SIG-001"], "pubkey": "test.pub",
      "description": "Evidence edited and manifest regenerated, but the signature cannot be."}),
]


def write_symlink_tarball(vector: Path) -> None:
    """BND-001: an archive containing a symbolic link. Byte-deterministic (fixed mtimes)."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(EXAMPLE.rglob("*")):
            info = tarfile.TarInfo(f"bundle/{path.relative_to(EXAMPLE).as_posix()}")
            info.mtime = 0
            if path.is_dir():
                info.type, info.mode = tarfile.DIRTYPE, 0o755
                tar.addfile(info)
            else:
                data = path.read_bytes()
                info.size, info.mode = len(data), 0o644
                tar.addfile(info, io.BytesIO(data))
        link = tarfile.TarInfo("bundle/escape")
        link.type, link.linkname, link.mtime = tarfile.SYMTYPE, "../../etc/passwd", 0
        tar.addfile(link)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0) as gz:
        gz.write(raw.getvalue())
    (vector / "bundle.tar.gz").write_bytes(compressed.getvalue())


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for group, name, mutate, expected in VECTORS:
        vector = OUT / group / name
        shutil.copytree(EXAMPLE, vector / "bundle")
        if mutate is not None:
            mutate(vector / "bundle")
        if expected.get("pubkey"):
            shutil.copy(PUBKEY, vector / expected["pubkey"])
        dump(vector / "expected.json", expected)
    vector = OUT / "invalid" / "bnd-001-symlink-in-archive"
    vector.mkdir(parents=True)
    write_symlink_tarball(vector)
    dump(vector / "expected.json", {"result": "failed", "rules": ["BND-001"],
                                     "description": "The archive contains a symbolic link."})
    print(f"wrote {len(VECTORS) + 1} vectors to {OUT.relative_to(SPEC_ROOT)}")


if __name__ == "__main__":
    main()
