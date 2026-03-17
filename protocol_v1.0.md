# QSP Protocol v1.0 (Frozen) — Stage205

MIT License © 2025 Motohiro Suzuki

## 0. Status of This Document
This document defines **QSP Protocol v1.0** as a frozen specification at Stage205.
Any change MUST be made in a subsequent stage (Stage206+) with explicit justification in:
- `analysis/assumptions.md`
- `analysis/break_analysis.md`
- `analysis/attack_claim_state_matrix.md`

## 1. Goals (Design Intent)
- Make security assumptions explicit and reviewable.
- Ensure fail-closed behavior on inconsistency, downgrade, replay, or state violation.
- Treat QKD as an optional entropy source (never an unconditional security upgrade).
- Provide a deterministic mapping from protocol states to acceptable messages and transitions.

## 2. Non-Goals
- Proving or extending QKD security proofs.
- Defining new cryptographic primitives.
- Guaranteeing availability under network loss or adversarial disruption.

## 3. Threat Model (Adversary)
The adversary MAY:
- intercept/modify/replay messages,
- attempt downgrade of algorithms/key sources,
- attempt transcript confusion across sessions,
- cause loss/failure of QKD and/or network resources.

The adversary MUST NOT:
- forge signatures (see assumptions),
- break the underlying hardness assumptions of selected PQC primitives (see assumptions).

## 4. Entities and Roles
- Initiator (I)
- Responder (R)

## 5. Notation
- `sid`: session identifier (unique per session)
- `epoch`: monotonically increasing counter per session
- `th`: transcript hash (hash over ordered handshake messages)
- `K_src`: key material from entropy sources (PQC-only and optionally QKD)
- `K_mix`: mixed key derived from sources via HKDF
- `K_aead`: AEAD traffic keys derived from `K_mix`

## 6. Protocol Overview (High-Level)
QSP establishes a session with:
1) authenticated handshake,
2) key source selection + mixing,
3) traffic key derivation,
4) protected application data,
5) rekey under policy conditions.

Core properties:
- Any mismatch in `sid/epoch/th/policy` MUST result in fail-closed.
- Downgrade attempts MUST be detected and rejected.

## 7. State Machine (Normative)
Normative states are defined in `spec/state_machine.md`.
This document references the state machine as authoritative.

## 8. Handshake Messages (Normative)
Wire-level fields are specified in `spec/wire_format.md`.

### 8.1 ClientHello (I -> R)
Purpose:
- propose algorithms and key sources
- bind an initial transcript

### 8.2 ServerHello (R -> I)
Purpose:
- select algorithms and key sources
- provide server authentication and transcript binding

### 8.3 Finished / Confirm (Both)
Purpose:
- confirm transcript and establish session keys
- finalize `sid` and `epoch=0`

## 9. Key Sources and Mixing (Normative)
### 9.1 Key Sources
- PQC-only source: MUST be supported
- QKD source: OPTIONAL; may be absent/fail

### 9.2 Mixing Rule
All available sources are combined into `K_mix` using HKDF with domain separation.

Normative requirement:
- If QKD is absent or fails, the protocol MUST remain secure as PQC-only (no false security claims).

## 10. Rekey (Normative)
Rekey may occur when:
- epoch threshold reached,
- policy requires refresh,
- drift/attack indicators are detected.

Rekey MUST:
- increase `epoch` monotonically,
- bind new keys to updated transcript/policy state,
- fail-closed on inconsistency.

## 11. Fail-Closed Semantics (Normative)
The implementation MUST immediately transition to CLOSED (or equivalent terminal failure)
when any of the following occur:
- transcript hash mismatch,
- unexpected message for current state,
- sid mismatch,
- epoch rollback or non-monotonicity,
- downgrade attempt detected,
- policy violation.

## 12. Security Claims (Informative Anchor)
Frozen claims are listed in `claims/claims.yaml`.
Attack mapping is in `analysis/attack_claim_state_matrix.md`.

## 13. Assumptions (Normative Reference)
Assumptions are enumerated in `analysis/assumptions.md`.

## 14. What Breaks If X Fails? (Normative Reference)
Failure impact enumeration is in `analysis/break_analysis.md`.

