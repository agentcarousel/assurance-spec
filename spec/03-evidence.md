# 3. Evaluation evidence

Schema: [`evidence.schema.json`](../schemas/0.1/evidence.schema.json). File name inside a bundle:
`evidence.json`.

An evidence document records **exactly one evaluation run** of one configuration (INV-5). It MUST
NOT contain values computed from other runs, such as trends, history windows, or baselines. A
producer may ship such values in other files of the bundle, labelled as derived.

## 3.1 Structure

| Property | Content |
|---|---|
| `spec` | `{"name": "agentcarousel-spec/evidence", "version": "0.1.x"}` |
| `subject` | `agent` (section 1.2) and `configuration` (section 1.3) |
| `execution` | `run_id`, `mode` (`mock`, `live`, or `batch`), producing `implementation`, timestamps, `repetitions`, `environment` |
| `disclosure` | What sensitive material the bundle carries (section 3.5) |
| `cases` | One entry per case **defined by the suite**, executed or not |
| `summary` | Counts by status, plus `critical_failures` |
| `limitations` | Machine-readable statements of what the evidence does not show |

## 3.2 Cases

Every case defined by the suite MUST appear exactly once, so `cases.length` equals
`test_suite.case_count`.

| `status` | Meaning |
|---|---|
| `passed` | Executed, and every assertion that applies passed the producer's threshold |
| `failed` | Executed, and at least one assertion failed |
| `error` | Execution failed. The agent's behavior was not evaluated |
| `timed_out` | Execution exceeded its time limit |
| `flaky` | Executed several times, with different outcomes |
| `not_tested` | Not executed. `not_tested_reason` is REQUIRED, and `assertions` MUST be empty |

`critical` is true when the case carries any critical assertion or its suite designates it
critical.

`trace_sources` declares where the execution trace came from (INV-3):

- `model_output`:
  - `observed`: from the model under test.
  - `mock`: supplied by a fixture or mock.
  - `none`: no output was produced.
- `tool_calls`:
  - `observed`: the agent emitted the calls and the producer captured them, for example from
    OpenTelemetry `execute_tool` spans.
  - `fixture_expectation`: the producer synthesized the steps from the test's own expected tool
    sequence.
  - `none`: the case involves no tool calls.

A `fixture_expectation` tool trace shows nothing about what the agent would call. Assertions
evaluated against it check the test's internal consistency, not the agent's behavior.

## 3.3 Assertions

Each assertion records:

- `kind`: a registered value or an `x-` extension.
- `evaluator_class` (INV-4):
  - `deterministic`: a rule or pattern check.
  - `golden`: comparison with a reference output.
  - `process`: an external program decided.
  - `llm_judge`: a language model decided.
- `outcome`: `pass`, `fail`, `error`, or `not_evaluated`.
- `score`, `weight`, `critical`: optional.

When a judge falls back to a deterministic check for a rubric item, the producer MUST report that
item's `evaluator_class` as `deterministic`.

## 3.4 Limitations

| Code | MUST be present when (semantic rule) |
|---|---|
| `tool_calls_not_observed` | Any case has `trace_sources.tool_calls = fixture_expectation` (SEM-003) |
| `judge_only_assertion` | A critical case has assertions and every one is `llm_judge`. The case id is listed in `cases` (SEM-004) |
| `mock_execution` | `execution.mode = mock` (SEM-005) |
| `partial_suite` | `summary.not_tested > 0` (SEM-006) |

Producers MAY add other limitations using `x-` codes. Every limitation carries a human-readable
`detail` and MAY list the `cases` it applies to.

## 3.5 Disclosure (INV-7)

- `system_prompt`:
  - `digest_only`: the prompt is withheld, and `configuration.system_prompt.digest` is REQUIRED.
  - `included`: the prompt was deliberately disclosed in the bundle.
  - `not_applicable`: the configuration has no separate system prompt.
- `test_inputs`:
  - `included`: case inputs appear verbatim.
  - `redacted`: system messages and detected secrets are replaced by digests or markers.
  - `excluded`: no case inputs appear.

The default for producers MUST be `digest_only`, and `redacted` or `excluded`. Disclosing more is
an explicit choice the producer records here.

## 3.6 Semantic rules

Verifiers MUST check these rules in addition to the schema. Rule ids appear in verifier output.

| Rule | Check |
|---|---|
| SEM-001 (INV-1) | `summary.total = cases.length = test_suite.case_count`, and each status count equals the number of cases with that status |
| SEM-002 (INV-2) | `summary.critical_failures` equals the number of critical cases whose status is `failed`, `error`, `timed_out`, or `flaky` |
| SEM-003 (INV-3) | See section 3.4 |
| SEM-004 (INV-4) | See section 3.4 |
| SEM-005 | See section 3.4 |
| SEM-006 (INV-1) | See section 3.4 |
| SEM-007 (INV-4) | If any assertion is `llm_judge`, `configuration.judge` is present |
| SEM-008 | Case ids are unique |
