# Contributing

- **Clarifications, typos, and schema bugs:** open a pull request.
- **Normative changes** (new fields, new rules, changed semantics): open an RFC using
  [rfcs/0000-template.md](rfcs/0000-template.md).
- **New implementations:** open an issue with a link to your code and to its results on
  `conformance/vectors`.

Every schema change must keep `uvx check-jsonschema@0.38.2 --check-metaschema schemas/0.1/*.json`
passing, and must update the conformance vectors when the change affects validity.

All participation follows the [Code of Conduct](CODE_OF_CONDUCT.md).
