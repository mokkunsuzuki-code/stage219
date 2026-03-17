# Claim → Test → Evidence Mapping

This document links security claims to executable tests and their evidence.

---

## Claim A2 – Replay Attack Resistance

Claim  
Replay attacks against session establishment are rejected.

Test  
tests/test_replay.py

Evidence  
evidence/replay_attack.log

Expected Result  
Session is rejected and connection terminates.

---

## Claim A3 – Downgrade Protection

Claim  
Downgrade attempts to weaker crypto parameters fail.

Test  
tests/test_downgrade.py

Evidence  
evidence/downgrade_attack.log

Expected Result  
Handshake fails.

---

## Claim A4 – Fail Closed Behaviour

Claim  
Protocol fails closed when security assumptions break.

Test  
tests/test_fail_closed.py

Evidence  
evidence/fail_closed.log

Expected Result  
Session terminates safely.

---

## Claim A5 – Session Integrity

Claim  
Session state integrity is preserved.

Test  
tests/test_session_integrity.py

Evidence  
evidence/session_integrity.log

Expected Result  
State validation passes.

