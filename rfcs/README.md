# RFC process

1. Copy `0000-template.md` to `NNNN-short-title.md`, using the next free number, and open a pull
   request.
2. The RFC stays open for public comment for at least 14 days. Implementers' objections are
   answered in the RFC text.
3. Maintainers (Stage 1) or the steering group (Stage 2) record the decision in the RFC header:
   `accepted`, `rejected`, or `postponed`, with a rationale.
4. An accepted RFC is merged together with its schema changes and conformance vectors. A normative
   change without vectors is not accepted.

## Planned RFCs

| Topic | Notes |
|---|---|
| Assurance profiles and dimensions | Depends on observed tool calls. See spec/07 |
| Normative portable test-definition format | Reconcile AgentCarousel fixtures and TEVV-Athlon. See spec/02 |
| DSSE-native signing and key discovery | Ed25519, ECDSA-P256, and Sigstore keyless |
| Final name and identifier hosting | Requires trademark and collision search |
