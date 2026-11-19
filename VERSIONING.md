# Versioning and deprecation

- **Specification versions** follow Semantic Versioning. Before 1.0, a minor version (0.x) MAY
  break compatibility, and the CHANGELOG lists every break.
- **Schema identifiers** carry the minor version: `…/schemas/0.1/…`. A patch release (0.1.x) only
  clarifies text or fixes schema bugs that no conformant document could have relied on.
- **Documents declare their version**, for example `spec.version` in `evidence.json` or the
  version suffix of an in-toto `predicateType`. Verifiers MUST reject major or minor versions they
  do not implement, and MUST NOT guess.
- **Deprecation:** after 1.0, a feature is marked deprecated for at least one minor release and six
  months before it is removed.
- **Identifier base:** moving from `https://assurance-spec.invalid/` to the final hosted base is
  recorded in the CHANGELOG. It does not change semantics.
