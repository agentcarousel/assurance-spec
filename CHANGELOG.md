# Changelog

## [Unreleased] — 0.1.0-draft

### Added
- Architecture and technical charter v0.1, with honesty invariants INV-1 to INV-8.
- Specification prose: identity, test definitions (informative), evidence, attestation,
  verification, security and privacy, trust and freshness (sketch), and interoperability mappings.
- JSON Schemas (2020-12): agent, evidence, evidence manifest, agent-evaluation predicate, and
  statement.
- Governance, versioning, RFC process, security policy, and contribution guide.
- Conformance kit: a separate Python verifier (`conformance/verify.py`, with pure-Python minisign
  `Ed`/`ED` verification), 19 valid and invalid vectors with expected rule ids, and a generator.
- Signed example bundle from a mock run of the reference CLI (`examples/mock-bundle`).
- CI: metaschema check, vectors, example verification, and vector freshness.
