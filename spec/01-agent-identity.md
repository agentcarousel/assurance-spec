# 1. Agent and configuration identity

Schema: [`agent.schema.json`](../schemas/0.1/agent.schema.json). The configuration is defined
under `$defs/configuration` in [`evidence.schema.json`](../schemas/0.1/evidence.schema.json).

## 1.1 Three identities

| Identity | Answers | Where it lives |
|---|---|---|
| Agent | Which logical agent is this? | `subject.agent` |
| Configuration | Exactly what was evaluated? | `subject.configuration` |
| Evidence | Which run, and which bundle? | `execution.run_id` and the bundle's digests |

A producer MUST NOT encode configuration (model, prompt, tools) in the agent `id`. The same
logical agent may be evaluated under many configurations.

## 1.2 Agent identity

- `id` is REQUIRED. It MUST be an absolute URI, and it SHOULD stay stable for the life of the
  logical agent.
- A producer with no naming authority of its own SHOULD use a `tag:` URI ([RFC 4151]), for example
  `tag:example.com,2026:agent/vulnerability-remediator`.
- `version` identifies a release of the logical agent. It is not a model version.
- `tools` lists the tools the agent is *permitted* to call, with their granted `scopes`. It
  declares intent. Behavior under test is shown by trace evidence (section 3).
- `external_ids` links the agent to records in other systems, such as asset inventories or GRC
  platforms, so consumers can join evidence to their own records without a shared registry.
- `owner` names an accountable team or organization. It SHOULD NOT be a personal email address.

## 1.3 Configuration identity

The configuration identity is the tuple:

- `model` (`provider`, `name`, and `snapshot` when the provider reports one)
- `system_prompt.digest`
- `test_suite.files[*].digest`
- `golden_files[*].digest`
- `judge` (`model`, `temperature`)

A producer MUST record each element that applied to the run. `model` is REQUIRED for `live` and
`batch` runs.

Two pieces of evidence describe the same configuration only if every recorded element is equal.
Consumers use this rule to decide freshness ([07-trust-profiles.md](07-trust-profiles.md)).

[RFC 4151]: https://www.rfc-editor.org/rfc/rfc4151
