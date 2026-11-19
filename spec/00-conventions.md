# 0. Conventions

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**,
**SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described in
BCP 14 ([RFC 2119], [RFC 8174]) when, and only when, they appear in all capitals.

- **Producer:** software that runs an evaluation and writes evidence.
- **Verifier:** software that checks a bundle's integrity, authenticity, and conformance.
- **Consumer:** software or a person that relies on verified evidence, for example a governance
  platform or an assessor.
- **Bundle:** a gzip-compressed tar archive with one top-level directory that holds
  `MANIFEST.json`, the documents it lists, and optionally a detached signature.

## Identifiers

Every machine-readable identifier in this draft uses the base URI in
[`../schemas/BASE_URI`](../schemas/BASE_URI). That base is `https://assurance-spec.invalid/`,
which is reserved by RFC 2606 and never resolves. Verifiers MUST NOT attempt to dereference it
(INV-6). The base will change once the identifiers are hosted. That change will be recorded in the
CHANGELOG and is not a semantic change.

## Digests

Within evidence documents and the manifest, a digest is the lowercase hex SHA-256 of the exact
bytes, prefixed with `sha256:`. In in-toto statements, digests follow the in-toto `DigestSet`
form, `{"sha256": "<hex>"}`.

## Extensions

Objects that allow extensions accept properties whose names begin with `x-`. Consumers MUST
ignore extensions they do not understand. Extensions MUST NOT change the meaning of standard
properties.

[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
[RFC 8174]: https://www.rfc-editor.org/rfc/rfc8174
