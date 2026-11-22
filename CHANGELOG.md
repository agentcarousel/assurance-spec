# Changelog

## [Unreleased] — 0.1.0-draft

### Changed
- Licensed under MIT throughout (`LICENSE`). Replaces Apache-2.0 OR MIT for schemas, code and
  test vectors, and CC BY 4.0 for the specification prose.
- Named the **AgentCarousel Specification**, replacing the working codename.
- Identifiers moved to the base `https://agentcarousel.com/spec/`: schema `$id`s,
  `predicateType` `https://agentcarousel.com/spec/predicates/agent-evaluation/v0.1`, and
  `spec.name` `agentcarousel-spec/evidence`. The provisional base `https://assurance-spec.invalid/`,
  emitted only by AgentCarousel CLI 0.9.0, is retired; documents that use it are an unsupported
  draft. The example bundle and conformance vectors were regenerated with AgentCarousel CLI 0.9.1.

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
