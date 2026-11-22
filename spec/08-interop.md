# 8. Interoperability mappings

## 8.1 OpenTelemetry GenAI semantic conventions

The GenAI conventions are maintained in `open-telemetry/semantic-conventions-genai` and are at
Development stability. Mappings are informative and pinned to the convention version the producer
used. Producers SHOULD record that version as an extension, for example
`x-otel-semconv-version`.

| OTel span (`gen_ai.operation.name`) | Evidence |
|---|---|
| `invoke_agent` | One case execution. The span's trace id MAY be recorded as an `x-` extension on the case |
| `chat` (child of `invoke_agent`) | Model output. Sets `trace_sources.model_output = observed` |
| `execute_tool`, with `gen_ai.tool.name` and `gen_ai.tool.call.id` | One observed tool call. When every tool call in a case comes from these spans, set `trace_sources.tool_calls = observed` |
| `create_agent` | Not mapped. Agent identity is declared, not inferred from telemetry |

## 8.2 [in-toto](https://in-toto.io/) `test-result/v0.1`

For consumers that only understand the generic predicate, a producer MAY emit an additional
statement:

| `test-result/v0.1` field | Source |
|---|---|
| `result` | `FAILED` if `summary.failed + error + timed_out > 0` or `critical_failures > 0`. Otherwise `WARNED` if `flaky + not_tested > 0` or any limitation is present. Otherwise `PASSED` |
| `configuration` | ResourceDescriptors for the suite files and the system prompt digest |
| `passedTests`, `failedTests`, `warnedTests` | Case ids by status. `flaky` and `not_tested` go in `warnedTests` |
| subject | Same as the agent-evaluation statement |

This mapping loses information, because the generic predicate has no field for limitations. The
agent-evaluation predicate is authoritative.

## 8.3 OSCAL Assessment Results

Evidence maps to an OSCAL Assessment Results document as follows:

- **Observation:** one per case, with `methods`:
  - `TEST` for `deterministic` and `golden`
  - `EXAMINE` for `llm_judge`
  - `TEST` for `process`, with the evaluator class in a namespaced prop
- **Finding:** one per mapped control, aggregating the related observations.
- **Risk:** one per limitation that affects a mapped control.

Custom properties MUST use a namespace (`ns`) under the identifier base. Control mappings MUST pin
the catalog and version (for example, NIST AI RMF 1.0).

## 8.4 TEVV-Athlon

An Athlon block's native events reference suite cases by tag. Producers implementing an Athlon plan
SHOULD keep the Athlon tags in `cases[*].tags`, so consumers can aggregate evidence per block
without the producer's tooling.
