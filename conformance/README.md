# Conformance kit

| File | Purpose |
|---|---|
| [`verify.py`](verify.py) | An independent verifier for [spec/05-verification.md](../spec/05-verification.md). It is written separately from the reference CLI, uses only the spec text and schemas, and needs no network. |
| [`vectors/`](vectors/) | Valid and invalid bundles. Each `expected.json` gives the result and the rule ids a verifier must report. |
| [`make_vectors.py`](make_vectors.py) | Regenerates `vectors/` from [`examples/mock-bundle`](../examples/). |

```bash
uv run --script conformance/verify.py BUNDLE.tar.gz --minisign-pubkey KEY.pub
uv run --script conformance/verify.py --vectors conformance/vectors
```

## How the vectors are built

Each invalid vector applies **one** mutation to the signed example bundle. When a rule
concerns the content of the documents (SCH, SEM, XDOC), the generator also rebuilds the
in-toto statement and `MANIFEST.json` to match the mutation, and drops the signature. That
reproduces what a producer, or a forger without the signing key, can always do. Those vectors
therefore pass integrity and fail only on the rule under test. `sig-001-forged-after-signing`
keeps the original signature to show that such forgery fails once a key is checked.

| Rule family | Result | Meaning |
|---|---|---|
| BND-001…004, SIG-001 | `failed` | The bundle cannot be trusted at all |
| BND-005, SCH-001, SEM-*, XDOC-* | `nonconformant` | The bundle is intact, but its documents break the spec |

## Implementations checked against these vectors

| Implementation | Result |
|---|---|
| `conformance/verify.py` | 19/19 |
| AgentCarousel CLI `agc verify` (0.9.1) | 19/19 results agree. The CLI reports rule ids for SCH/SEM/XDOC/BND-005 failures, and descriptive messages for integrity failures |

Both implementations are maintained by AgentCarousel, so their agreement is not yet
*independent* evidence ([CHARTER §11](../CHARTER.md#11-roadmap-and-release-gates)). A verifier
written by another party is the most valuable contribution this project can receive.
