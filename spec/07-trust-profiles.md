# 7. Trust, profiles, and freshness (non-normative sketch)

This section records the intended model so that v0.1 documents do not conflict with it. Normative
text will come through RFCs.

## 7.1 Three separate concepts

1. **Evidence status** is mechanical: `none`, `integrity_only`, `verified`, or `nonconformant`
   (section 5).
2. **Assurance profile** is a named, versioned set of requirements for a class of agent, such as:
   - informational agents
   - tool-using agents
   - agents handling sensitive data
   - agents taking autonomous actions
   - agents operating critical systems

   Profiles are not ascending levels. A profile states, for example, which assertion kinds must be
   deterministic, the minimum suite coverage per threat category, whether tool calls must be
   `observed`, and the maximum evidence age measured in configuration changes.
3. **Assurance determination** is one evaluator's conclusion that specific evidence does or does
   not meet a specific profile version:
   - meets
   - meets with exceptions
   - does not meet
   - insufficient evidence
   - stale

   A determination names the evaluator, the profile version, the evidence digests it relied on,
   and its exceptions. A relying party can always apply a stricter policy.

## 7.2 Dimensions

Separate assurance dimensions are planned, for example:

- behavioral reliability
- security resilience
- authorization integrity
- tool safety
- data protection
- operational reliability

Each dimension must cite the cases that contribute to it. v0.1 deliberately defines **no dimension
scores**. Authorization integrity and tool safety cannot be measured honestly until tool calls are
`observed` (INV-3).

## 7.3 Freshness

Evidence is **stale** for a deployed configuration when any element of the configuration identity
(section 1.3) differs from what the evidence records. Changing the model snapshot, editing the
prompt, adding a tool, or changing the suite all make evidence stale.

Calendar age alone is a policy choice, not a freshness rule. Producers and registries that track
re-evaluation SHOULD key it on configuration digests.

## 7.4 Registries

A registry is an optional index of bundles and determinations. It is never required for
verification (INV-6), and listing in a registry is not a determination. A registry SHOULD:

- re-run the verification procedure on ingest;
- refuse promotion of runs with `not_tested > 0` unless a profile allows partial suites;
- mark entries stale when a newer configuration identity is published for the same agent.
