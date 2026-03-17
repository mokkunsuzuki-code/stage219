# Security Assumptions

QSP relies on the following assumptions.

A1: PQC shared secret is unpredictable
A2: HKDF behaves as a pseudorandom function
A3: AES-GCM provides authenticated encryption
A4: QKD key (if used) provides entropy
A5: Session preconditions are enforced (fail-closed)
