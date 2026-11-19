# Security policy

Report vulnerabilities in the specification, the schemas, or the conformance verifier through a
[private GitHub security advisory](https://github.com/agentcarousel/assurance-spec/security/advisories/new).
Do not open a public issue.

In scope:

- A verification bypass, where a tampered or forged bundle reaches `verified`.
- An honesty-invariant bypass, where a misleading bundle reaches `verified` without being reported
  `nonconformant`.
- Unsafe archive handling in a verifier.
- Disclosure defaults that leak sensitive material.

We aim to acknowledge reports within five business days.
