# AgentCarousel Specification

The AgentCarousel Specification is an open, vendor-neutral specification for **portable,
independently verifiable evidence about how an AI agent behaved under test**.

A producer runs an evaluation and writes a bundle. Anyone else can check that bundle offline,
without the producer's tools, a model vendor, or a registry. The check confirms what was tested,
against which configuration, by which method, with what result, and what was *not* tested.

> **Status: draft 0.1. Not stable.** Identifiers use the base `https://agentcarousel.com/spec/`.
> They are names: verifiers never fetch them.

## Read first

- [CHARTER.md](CHARTER.md): mission, architecture, honesty invariants, and the gap between the
  reference implementation and the spec.
- [spec/](spec/): the normative text. Start with [conventions](spec/00-conventions.md).
  1. [Agent and configuration identity](spec/01-agent-identity.md)
  2. [Test definitions](spec/02-test-definitions.md) (informative in 0.1)
  3. [Evaluation evidence](spec/03-evidence.md)
  4. [Bundles and attestation](spec/04-attestation.md)
  5. [Verification procedure](spec/05-verification.md)
  6. [Security and privacy](spec/06-security-privacy.md)
  7. [Trust, profiles, and freshness](spec/07-trust-profiles.md) (sketch)
  8. [Interoperability mappings](spec/08-interop.md)
- [schemas/0.1/](schemas/0.1/): JSON Schema 2020-12.

## What a bundle contains

```
agentcarousel-evidence-<run>/
├── MANIFEST.json             # SHA-256 of every other file
├── MANIFEST.json.minisig     # optional detached signature
├── evidence.json             # one run: subject, cases, summary, limitations
├── attestation.intoto.json   # in-toto Statement v1 over the tested artifacts
└── …                         # producer-specific files (informative)
```

## Implementations

| Role | Implementation | Status |
|---|---|---|
| Producer and verifier (reference) | [AgentCarousel CLI](https://github.com/agentcarousel/agentcarousel) (`agc export`, `agc verify`) | Emits and verifies v0.1 from agc 0.9.1; agrees with `verify.py` on all vectors. See [CHARTER.md §6](CHARTER.md#6-reference-implementation-status) |
| Verifier (Python, separate implementation) | [`conformance/verify.py`](conformance/) | Passes all 19 [conformance vectors](conformance/vectors/) |

Implementations that are independent of AgentCarousel are the main goal of this project. Please
open an issue to be listed.

## Try it

```bash
uv run --script conformance/verify.py examples/mock-bundle --minisign-pubkey examples/mock-bundle.pub
uv run --script conformance/verify.py --vectors conformance/vectors
```

## License

[MIT](LICENSE), for everything in this repository: the specification text, schemas, code, and test
vectors.
