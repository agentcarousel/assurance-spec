# 6. Security and privacy

## 6.1 Disclosure defaults (INV-7)

Producers MUST, by default:

- withhold system prompts and record only their digests (`disclosure.system_prompt = digest_only`);
- replace system messages in recorded case inputs with digests, and remove detected credentials
  (`disclosure.test_inputs = redacted`);
- withhold derived artifacts that reproduce prompt text, such as suggested prompt rewrites.

Disclosing more MUST require an explicit producer action, and the result MUST be recorded in
`disclosure`. Publishing a bundle to any registry follows the same defaults.

Test suites built on real personal data, protected health information, or customer content
SHOULD NOT be used to produce evidence intended for exchange. Synthetic data is RECOMMENDED.

## 6.2 Bundle handling

Verifiers treat bundles as untrusted input. Section 5, step 1, lists the archive checks. Verifiers
also MUST:

- bound decompressed size and file count;
- never execute bundle content;
- never dereference URIs found in bundles.

## 6.3 Keys

Producers hold their own signing keys. A registry or hosted service MUST NOT be required to hold
or vouch for producer keys. Key distribution and revocation are the relying party's trust policy.
A future RFC may standardize key discovery. It will not make discovery mandatory for verification.

## 6.4 Threats this specification does not address

- **A dishonest producer.** A producer can run a weak suite honestly, or falsify a run outright.
  Signatures prove origin, not truthfulness. Independent re-execution and assessor determinations
  ([07-trust-profiles.md](07-trust-profiles.md)) address this.
- **Suite overfitting.** An agent tuned to pass a known suite. Holdout suites and suite rotation
  are profile concerns.
- **Behavior in production.** Evidence describes behavior under test. Runtime monitoring is out of
  scope.

## 6.5 Reporting vulnerabilities

See [`../SECURITY.md`](../SECURITY.md).
