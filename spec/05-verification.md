# 5. Verification procedure

A verifier needs only the bundle, the schemas in [`schemas/0.1/`](../schemas/0.1/), and,
optionally, a public key it already trusts. It MUST NOT use the network (INV-6). Each step names
the rule id reported on failure.

1. **Unpack safely (BND-001).** Reject the bundle if it has more than one top-level directory, any
   absolute path, any `.` or `..` path segment, a symbolic or hard link, a device file, or a path
   that escapes the top-level directory.
2. **Manifest (BND-002).** Parse `MANIFEST.json` and validate it against the manifest schema.
3. **Completeness (BND-003).** The set of regular files, excluding `MANIFEST.json` and
   `MANIFEST.json.minisig`, MUST equal the set of manifest `path`s.
4. **Integrity (BND-004).** Each file's SHA-256 MUST equal its manifest entry.
5. **Signature (SIG-001).** If the verifier has a trusted key, `MANIFEST.json.minisig` MUST exist
   and verify, including the global signature over the trusted comment. If the verifier has no key,
   skip this step and do not report the result as authenticated.
6. **Required documents (BND-005).** `evidence.json` and `attestation.intoto.json` MUST be present
   and listed.
7. **Schemas (SCH-001).** Validate `evidence.json` and `attestation.intoto.json` against their
   schemas, resolving `$ref`s locally only.
8. **Semantics (SEM-001 … SEM-008).** Apply the rules in [03-evidence.md §3.6](03-evidence.md#36-semantic-rules).
9. **Cross-document consistency (XDOC-001 … XDOC-003).**
   - XDOC-001: `predicate.evidence_documents` contains `evidence.json`, and every listed digest
     equals the file's actual digest.
   - XDOC-002: `predicate.agent`, `configuration`, `summary`, and `limitations` equal those in
     `evidence.json`. `predicate.run_id` equals `execution.run_id`.
   - XDOC-003: the statement subjects are exactly the suite files plus the system prompt, if
     present, with digests matching the configuration.

## 5.1 Result

| Result | Condition |
|---|---|
| `verified` | All steps pass, and step 5 ran with a trusted key |
| `integrity_only` | All steps pass, and step 5 was skipped |
| `nonconformant` | Steps 1–5 pass, but a schema, semantic, or cross-document rule fails |
| `failed` | Any of steps 1–5 fails |

`verified` means the bundle is intact, comes from the key holder, and is internally honest under
this specification. It says nothing about whether the agent is safe, and nothing about whether the
evaluation design was adequate. Those are questions for assurance profiles and determinations
([07-trust-profiles.md](07-trust-profiles.md)).
