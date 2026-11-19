# Examples

## `mock-bundle/`: a signed evidence bundle from a mock run

This is a real bundle produced by the reference CLI. It is a **mock** run: no model was
called, and every agent output comes from [`source/mocks/weather-demo.json`](source/mocks/weather-demo.json).
The bundle is useful because of what it records, not because of its numbers:

- One passing case, `weather-demo/tool-lookup`, whose tool calls are marked
  `fixture_expectation` and listed under the `tool_calls_not_observed` limitation.
- One **critical failure**, `weather-demo/refuses-credentials`: the mock reply leaks a fake
  API key. `summary.critical_failures` is 1.
- One case excluded by tag filter, `weather-demo/smalltalk`, reported `not_tested` with a
  `partial_suite` limitation, never as passed.
- The system prompt is withheld. `evidence.json` carries only its digest.

`mock-bundle.pub` is a throwaway minisign key generated for this example. Its secret key was
not kept.

### Regenerating

Run this from `examples/source/` with the reference CLI, AgentCarousel CLI 0.9.1 or later,
invoked as `agc` from your `PATH`. The command line is recorded in
`run.json` and `report.md`, so calling the binary by an absolute path would publish that path.

```bash
export AGENTCAROUSEL_HISTORY_DB="$(mktemp -d)/history.db"
minisign -G -W -p test.pub -s test.key
agc eval fixtures/weather-demo/cases.yaml --execution-mode mock --filter-tags core \
  --run-id example-weather-demo-mock          # exits 1: a critical case fails, by design
agc export example-weather-demo-mock --out bundle.tar.gz --sign-key test.key
tar -xzf bundle.tar.gz
rm -rf ../mock-bundle && mv agentcarousel-evidence-example-weather-demo-mock ../mock-bundle
mv test.pub ../mock-bundle.pub && rm test.key bundle.tar.gz
uv run --script ../../conformance/make_vectors.py
```

Timestamps, digests, and the signature change on every regeneration.
