# 2. Test definitions (informative in v0.1)

v0.1 does **not** define a normative test-definition format. Evidence refers to a test suite by
`test_suite.id`, `version`, `case_count`, and the digest of every file in the suite. A verifier that
holds the suite files can confirm that the evidence was produced from them.

Two existing formats are expected to feed the normative definition, which will be developed
through the RFC process:

- **AgentCarousel fixtures.** A YAML format with cases, input messages, expected outputs
  (`contains`, `regex`, `json_path`, `golden_diff`, and similar), expected tool sequences with
  `strict`, `subsequence`, or `unordered` ordering, and weighted rubrics with optional
  deterministic `auto_check`s and `critical` items. The schema is published in the AgentCarousel
  repository.
- **TEVV-Athlon assessment plans** (NIST AI 200-2). These organize evaluation as goals → metrology
  blocks → events. A test suite implements events. A plan maps to an OSCAL Assessment Plan.

Requirements the normative format is expected to meet. These are input to the RFC, not
constraints on v0.1 producers:

1. Deterministic assertions can express every security-critical expectation without an LLM judge.
2. Prohibited tool calls and authorization boundaries are expressed directly, not only as
   negative output matches.
3. Each case can be marked critical.
4. Expected tool behavior is checked against **observed** tool calls (INV-3).
5. Human-approval requirements and failure or recovery behavior can be expressed.
