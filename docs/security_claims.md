# Security Claim Matrix

This document defines the relationship between protocol assumptions and the security guarantees provided by QSP.

The purpose of this matrix is to make the reasoning structure of the protocol explicit and reviewable.

If an assumption fails, the corresponding guarantees may no longer hold.

---

## Security Claim Table

| Assumption | Description | Guarantees |
|-----------|-------------|-----------|
| A1 | PQC shared secret unpredictability | Confidentiality |
| A2 | HKDF pseudorandomness | Secure key derivation |
| A3 | AES-GCM authenticated encryption | Message integrity and authenticity |
| A4 | QKD entropy (optional) | Additional entropy source |
| A5 | Fail-closed session enforcement | Safe protocol termination |

---

## Design Philosophy

QSP explicitly separates:

- **Assumptions** (what the protocol depends on)
- **Guarantees** (what security properties are achieved)

This improves:

- security review transparency
- threat analysis clarity
- reproducibility of security reasoning

---

## Interpretation

The matrix should be read as:

"If assumption Ai holds, the protocol can guarantee Gi."

If Ai fails, Gi may no longer hold.

This explicit structure prevents implicit security claims and helps reviewers identify the true trust boundaries of the system.

---

## Relation to Other Documents

- `security_assumptions.md` defines the assumptions.
- `threat_model.md` defines the attacker model.
- `guarantees.md` defines the protocol guarantees.

This document links them together.