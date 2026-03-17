#!/usr/bin/env bash
# MIT License © 2025 Motohiro Suzuki

set -euo pipefail

echo "== Stage214: Public Evidence Verification =="

if [ ! -f "evidence_bundle/evidence_bundle.json" ]; then
  echo "[ERROR] missing: evidence_bundle/evidence_bundle.json"
  exit 1
fi

if [ ! -f "signatures/evidence_bundle.sig" ]; then
  echo "[ERROR] missing: signatures/evidence_bundle.sig"
  exit 1
fi

if [ ! -f "keys/evidence_signing_public.pem" ]; then
  echo "[ERROR] missing: keys/evidence_signing_public.pem"
  exit 1
fi

python3 verification/verify_signature.py

echo
echo "[OK] public verification complete"
