# Changelog

## [Unreleased]

### Changed
- Removed an incorrect statement from CHARTER.md §7: it said AgentCarousel had submitted public
  comments on NIST AI 200-2. No comment was submitted on behalf of AgentCarousel.
- CHARTER.md §6 now lists the reference implementation's OSCAL Assessment Results as not aligned
  with [spec/08 §8.3](spec/08-interop.md#83-oscal-assessment-results).

## [0.1.0] — 2026-11-22 (draft)

First tagged release. Draft: nothing is stable before 1.0 (see [VERSIONING.md](VERSIONING.md)).

### Changed
- Reference implementation status refers to AgentCarousel CLI 0.10.1, the current release, which
  agrees with `conformance/verify.py` on all 19 vectors.
- The name **AgentCarousel Specification** and the identifier base are adopted; the planned RFC on
  the final name and identifier hosting is dropped.
- Mentions of in-toto link to https://in-toto.io/.
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
