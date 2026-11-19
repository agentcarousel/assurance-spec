# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.23",
#   "referencing>=0.35",
#   "cryptography>=43",
# ]
# ///
"""Independent verifier for agent assurance spec v0.1 evidence bundles.

Implements spec/05-verification.md without the AgentCarousel CLI or any network access.

    uv run --script conformance/verify.py BUNDLE [--minisign-pubkey KEY] [--json]
    uv run --script conformance/verify.py --vectors conformance/vectors

BUNDLE is a .tar.gz or an extracted bundle directory. Exit status: 0 for `verified` or
`integrity_only`, 1 for `nonconformant` or `failed`, 2 for usage errors.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SPEC_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = SPEC_ROOT / "schemas" / "0.1"
MANIFEST = "MANIFEST.json"
SIGNATURE = "MANIFEST.json.minisig"
EVIDENCE = "evidence.json"
STATEMENT = "attestation.intoto.json"
MAX_FILES = 10_000
MAX_TOTAL_BYTES = 512 * 1024 * 1024
FAILURE_STATUSES = {"failed", "error", "timed_out", "flaky"}


@dataclass
class Report:
    result: str = "integrity_only"
    signature: str = "absent"
    violations: list[tuple[str, str]] = field(default_factory=list)

    def add(self, rule: str, message: str) -> None:
        self.violations.append((rule, message))

    @property
    def rules(self) -> list[str]:
        return sorted({rule for rule, _ in self.violations})


class Fatal(Exception):
    """Integrity or signature failure: the bundle cannot be trusted at all."""

    def __init__(self, rule: str, message: str):
        super().__init__(message)
        self.rule = rule


# ── Step 1: safe unpacking ───────────────────────────────────────────────────


def unpack(archive: Path, dest: Path) -> Path:
    """Extract regular files only; reject links, devices, absolute or escaping paths (BND-001)."""
    total = 0
    tops: set[str] = set()
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) > MAX_FILES:
            raise Fatal("BND-001", "too many archive entries")
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
                raise Fatal("BND-001", f"unsafe path in archive: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise Fatal("BND-001", f"non-regular archive entry: {member.name}")
            tops.add(path.parts[0])
            total += member.size
            if total > MAX_TOTAL_BYTES:
                raise Fatal("BND-001", "archive too large")
        if len(tops) != 1:
            raise Fatal("BND-001", "bundle must have exactly one top-level directory")
        for member in members:
            target = dest.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())
    return dest / tops.pop()


def bundle_root(path: Path) -> Path:
    if (path / MANIFEST).is_file():
        return path
    children = [c for c in path.iterdir() if c.is_dir() and (c / MANIFEST).is_file()]
    if len(children) != 1:
        raise Fatal("BND-002", "MANIFEST.json not found (or more than one bundle)")
    return children[0]


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── Steps 2-4: manifest, completeness, integrity ─────────────────────────────


def check_manifest(root: Path, schemas: Schemas) -> dict[str, str]:
    try:
        manifest = json.loads((root / MANIFEST).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise Fatal("BND-002", f"MANIFEST.json unreadable: {exc}") from exc
    errors = schemas.errors("evidence-manifest.schema.json", manifest)
    if errors:
        raise Fatal("BND-002", f"MANIFEST.json invalid: {errors[0]}")

    listed: dict[str, str] = {}
    for entry in manifest["files"]:
        path = entry["path"]
        parts = PurePosixPath(path).parts
        if any(part in (".", "..") for part in parts):
            raise Fatal("BND-001", f"unsafe manifest path: {path}")
        if path in listed:
            raise Fatal("BND-002", f"duplicate manifest entry: {path}")
        listed[path] = entry["sha256"]

    present: set[str] = set()
    for item in root.rglob("*"):
        if item.is_symlink():
            raise Fatal("BND-001", f"symbolic link in bundle: {item.relative_to(root)}")
        if item.is_file():
            rel = item.relative_to(root).as_posix()
            if rel not in (MANIFEST, SIGNATURE):
                present.add(rel)
    if present != set(listed):
        missing = sorted(set(listed) - present)
        extra = sorted(present - set(listed))
        raise Fatal("BND-003", f"manifest/file mismatch; missing={missing} unlisted={extra}")

    for path, expected in listed.items():
        actual = "sha256:" + sha256_hex(root / path)
        if actual != expected:
            raise Fatal("BND-004", f"hash mismatch: {path}")
    return listed


# ── Step 5: minisign signature (pure Python) ────────────────────────────────


def verify_minisign(message: bytes, signature_text: str, pubkey_text: str) -> None:
    """Verify a minisign detached signature, legacy (Ed) or prehashed (ED)."""
    key_lines = [line for line in pubkey_text.splitlines() if line.strip()]
    key = base64.b64decode(key_lines[-1])
    if len(key) != 42 or key[:2] != b"Ed":
        raise Fatal("SIG-001", "unsupported minisign public key")
    key_id, public = key[2:10], key[10:]

    lines = signature_text.splitlines()
    if len(lines) < 4 or not lines[2].startswith("trusted comment: "):
        raise Fatal("SIG-001", "malformed minisign signature file")
    sig = base64.b64decode(lines[1])
    if len(sig) != 74:
        raise Fatal("SIG-001", "malformed minisign signature")
    algorithm, sig_key_id, signature = sig[:2], sig[2:10], sig[10:]
    if sig_key_id != key_id:
        raise Fatal("SIG-001", "signature was made with a different key")
    if algorithm == b"ED":
        signed = hashlib.blake2b(message, digest_size=64).digest()
    elif algorithm == b"Ed":
        signed = message
    else:
        raise Fatal("SIG-001", f"unsupported minisign algorithm {algorithm!r}")

    verifier = Ed25519PublicKey.from_public_bytes(public)
    trusted_comment = lines[2][len("trusted comment: ") :].encode()
    global_signature = base64.b64decode(lines[3])
    try:
        verifier.verify(signature, signed)
        verifier.verify(global_signature, signature + trusted_comment)
    except InvalidSignature as exc:
        raise Fatal("SIG-001", "minisign signature does not verify") from exc


# ── Step 7: schemas (local registry only) ───────────────────────────────────


class Schemas:
    def __init__(self, directory: Path):
        self.by_name: dict[str, dict] = {}
        registry: Registry = Registry()
        for path in sorted(directory.glob("*.schema.json")):
            schema = json.loads(path.read_text())
            self.by_name[path.name] = schema
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        self.registry = registry  # no retrieve function: unknown refs fail, never fetch

    def errors(self, name: str, document: object) -> list[str]:
        validator = Draft202012Validator(self.by_name[name], registry=self.registry)
        return [
            f"{'/'.join(str(p) for p in error.absolute_path) or '(root)'}: {error.message}"
            for error in validator.iter_errors(document)
        ]


# ── Step 8: semantic rules ──────────────────────────────────────────────────


def limitation_cases(evidence: dict) -> dict[str, set[str]]:
    codes: dict[str, set[str]] = {}
    for limitation in evidence.get("limitations", []):
        codes.setdefault(limitation["code"], set()).update(limitation.get("cases", []))
    return codes


def judge_only_critical(case: dict) -> bool:
    assertions = case.get("assertions", [])
    return bool(
        case.get("critical")
        and assertions
        and all(a["evaluator_class"] == "llm_judge" for a in assertions)
    )


def check_semantics(evidence: dict, report: Report) -> None:
    cases = evidence["cases"]
    summary = evidence["summary"]
    suite_count = evidence["subject"]["configuration"]["test_suite"]["case_count"]
    if not (summary["total"] == len(cases) == suite_count):
        report.add("SEM-001", "summary.total, cases, and test_suite.case_count differ")
    for status in ("passed", "failed", "error", "timed_out", "flaky", "not_tested"):
        actual = sum(1 for c in cases if c["status"] == status)
        if summary[status] != actual:
            report.add("SEM-001", f"summary.{status}={summary[status]} but {actual} case(s)")

    critical_failures = sum(
        1 for c in cases if c["critical"] and c["status"] in FAILURE_STATUSES
    )
    if summary["critical_failures"] != critical_failures:
        report.add("SEM-002", f"critical_failures should be {critical_failures}")

    codes = limitation_cases(evidence)
    if any(c["trace_sources"]["tool_calls"] == "fixture_expectation" for c in cases):
        if "tool_calls_not_observed" not in codes:
            report.add("SEM-003", "synthesized tool calls without tool_calls_not_observed")
    for case in cases:
        if judge_only_critical(case) and case["id"] not in codes.get("judge_only_assertion", set()):
            report.add("SEM-004", f"judge-only critical case {case['id']} not listed")
    if evidence["execution"]["mode"] == "mock" and "mock_execution" not in codes:
        report.add("SEM-005", "mock execution without mock_execution limitation")
    if summary["not_tested"] > 0 and "partial_suite" not in codes:
        report.add("SEM-006", "not_tested cases without partial_suite limitation")
    uses_judge = any(
        a["evaluator_class"] == "llm_judge" for c in cases for a in c.get("assertions", [])
    )
    if uses_judge and "judge" not in evidence["subject"]["configuration"]:
        report.add("SEM-007", "llm_judge assertions without configuration.judge")
    seen: set[str] = set()
    for case in cases:
        if case["id"] in seen:
            report.add("SEM-008", f"duplicate case id {case['id']}")
        seen.add(case["id"])


# ── Step 9: cross-document consistency ──────────────────────────────────────


def expected_subjects(configuration: dict) -> set[tuple[str, str]]:
    subjects = {
        (f["path"], f["digest"].removeprefix("sha256:"))
        for f in configuration["test_suite"]["files"]
    }
    prompt = configuration.get("system_prompt")
    if prompt:
        subjects.add((prompt.get("path", "system-prompt"), prompt["digest"].removeprefix("sha256:")))
    return subjects


def check_cross_documents(
    evidence: dict, statement: dict, listed: dict[str, str], report: Report
) -> None:
    predicate = statement["predicate"]
    documents = predicate["evidence_documents"]
    if not any(d["path"] == EVIDENCE for d in documents):
        report.add("XDOC-001", "evidence_documents does not list evidence.json")
    for document in documents:
        if document["path"] == MANIFEST:
            report.add("XDOC-001", "predicate references MANIFEST.json (circular digest)")
        elif listed.get(document["path"]) != document["digest"]:
            report.add("XDOC-001", f"digest mismatch for {document['path']}")
    pairs = {
        "agent": evidence["subject"]["agent"],
        "configuration": evidence["subject"]["configuration"],
        "summary": evidence["summary"],
        "limitations": evidence["limitations"],
    }
    for name, value in pairs.items():
        if predicate[name] != value:
            report.add("XDOC-002", f"predicate.{name} differs from evidence.json")
    if predicate["run_id"] != evidence["execution"]["run_id"]:
        report.add("XDOC-002", "predicate.run_id differs from execution.run_id")
    actual = {(s["name"], s["digest"]["sha256"]) for s in statement["subject"]}
    if actual != expected_subjects(evidence["subject"]["configuration"]):
        report.add("XDOC-003", "statement subjects are not exactly the tested artifacts")


# ── Driver ──────────────────────────────────────────────────────────────────


def verify(bundle: Path, pubkey: Path | None, schemas: Schemas) -> Report:
    report = Report()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            root = unpack(bundle, Path(tmp)) if bundle.is_file() else bundle_root(bundle)
            root = bundle_root(root)
            listed = check_manifest(root, schemas)
            signature_path = root / SIGNATURE
            if pubkey is not None:
                if not signature_path.is_file():
                    raise Fatal("SIG-001", "signature required but MANIFEST.json.minisig missing")
                verify_minisign(
                    (root / MANIFEST).read_bytes(),
                    signature_path.read_text(),
                    pubkey.read_text(),
                )
                report.signature = "valid"
            elif signature_path.is_file():
                report.signature = "present_unverified"
        except Fatal as fatal:
            report.result = "failed"
            report.add(fatal.rule, str(fatal))
            return report

        if EVIDENCE not in listed or STATEMENT not in listed:
            report.add("BND-005", "bundle must carry evidence.json and attestation.intoto.json")
        else:
            try:
                evidence = json.loads((root / EVIDENCE).read_text())
                statement = json.loads((root / STATEMENT).read_text())
            except json.JSONDecodeError as exc:
                report.add("SCH-001", f"invalid JSON: {exc}")
            else:
                for name, document in (
                    ("evidence.schema.json", evidence),
                    ("agent-evaluation-statement.schema.json", statement),
                ):
                    for error in schemas.errors(name, document):
                        report.add("SCH-001", f"{name}: {error}")
                if not report.violations:
                    check_semantics(evidence, report)
                    check_cross_documents(evidence, statement, listed, report)

    if report.violations:
        report.result = "nonconformant"
    elif report.signature == "valid":
        report.result = "verified"
    return report


def run_vectors(directory: Path, schemas: Schemas) -> int:
    """Each vector is a directory holding `bundle/` (or `bundle.tar.gz`) and `expected.json`."""
    failures = 0
    vectors = sorted(p.parent for p in directory.rglob("expected.json"))
    for vector in vectors:
        expected = json.loads((vector / "expected.json").read_text())
        pubkey = vector / expected["pubkey"] if expected.get("pubkey") else None
        tarball = vector / "bundle.tar.gz"
        report = verify(tarball if tarball.exists() else vector / "bundle", pubkey, schemas)
        ok = report.result == expected["result"] and set(expected.get("rules", [])) <= set(
            report.rules
        )
        status = "ok  " if ok else "FAIL"
        print(f"{status} {vector.relative_to(directory)}: {report.result} {report.rules}")
        failures += 0 if ok else 1
    print(f"{len(vectors) - failures}/{len(vectors)} vectors behaved as expected")
    return 1 if failures or not vectors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--minisign-pubkey", type=Path)
    parser.add_argument("--vectors", type=Path, help="run every vector under this directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    schemas = Schemas(SCHEMA_DIR)
    if args.vectors:
        return run_vectors(args.vectors, schemas)
    if args.bundle is None:
        parser.error("BUNDLE or --vectors is required")
    report = verify(args.bundle, args.minisign_pubkey, schemas)
    if args.json:
        print(
            json.dumps(
                {
                    "result": report.result,
                    "signature": report.signature,
                    "violations": [{"rule": r, "message": m} for r, m in report.violations],
                },
                indent=2,
            )
        )
    else:
        print(report.result)
        for rule, message in report.violations:
            print(f"  {rule}: {message}")
    return 0 if report.result in ("verified", "integrity_only") else 1


if __name__ == "__main__":
    sys.exit(main())
