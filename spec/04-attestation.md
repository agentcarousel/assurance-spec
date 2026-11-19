# 4. Bundles and attestation

## 4.1 Bundle layout

A bundle is a `.tar.gz` with exactly one top-level directory. That directory MUST contain:

| File | Schema | Notes |
|---|---|---|
| `MANIFEST.json` | [`evidence-manifest.schema.json`](../schemas/0.1/evidence-manifest.schema.json) | Lists **every** other file except its own signature |
| `evidence.json` | [`evidence.schema.json`](../schemas/0.1/evidence.schema.json) | Section 3 |
| `attestation.intoto.json` | [`agent-evaluation-statement.schema.json`](../schemas/0.1/agent-evaluation-statement.schema.json) | Section 4.2 |

It MAY contain:

- `MANIFEST.json.minisig`: a detached signature over `MANIFEST.json` (section 4.3).
- Any other files listed in the manifest, such as producer-native run records, reports, or OSCAL
  Assessment Results.

Files that are not standard are informative. Their presence does not change the meaning of
`evidence.json`.

## 4.2 In-toto statement

`attestation.intoto.json` is an in-toto Statement v1:

- `predicateType`: `https://assurance-spec.invalid/predicates/agent-evaluation/v0.1`
- `subject`: the **tested artifacts**, following in-toto's guidance for test results ("the source
  artifacts tested"):
  - one subject per `configuration.test_suite.files[*]`, named by its `path`
  - one subject for `configuration.system_prompt`, when present, named by its `path` or
    `system-prompt`
  - each subject's `digest.sha256` equals the hex of the corresponding configuration digest
- `predicate`:
  - `run_id`, `evaluated_at`, and `producer`
  - copies of `agent`, `configuration`, `summary`, and `limitations` that MUST equal those in
    `evidence.json`
  - `evidence_documents`: the digests of `evidence.json` and, optionally, other evidence documents

**No circular digests.** The predicate MUST NOT contain the digest of `MANIFEST.json`, because the
manifest lists the statement. Integrity flows one way:

```
signature → MANIFEST.json → attestation.intoto.json → evidence.json → tested artifacts
```

Consumers that only understand in-toto's generic `test-result/v0.1` predicate can map this one as
described in [08-interop.md](08-interop.md).

## 4.3 Signatures

v0.1 defines one signature mechanism: a [minisign] detached signature over the exact bytes of
`MANIFEST.json`, stored as `MANIFEST.json.minisig`.

- Both the legacy (`Ed`) and prehashed (`ED`) minisign algorithms are allowed.
- The signature covers the statement and the evidence through the digest chain above.

A bundle without a signature can be checked for integrity only. Signing keys belong to the
producer. Verifiers obtain public keys through their own trust policy, never by fetching them from
a URL inside the bundle.

**Planned for 0.2 (RFC):** a DSSE envelope around the statement, signed with Ed25519 or
ECDSA-P256 keys or with Sigstore keyless signing. With it, standard in-toto tooling can verify the
statement on its own.

[minisign]: https://jedisct1.github.io/minisign/
