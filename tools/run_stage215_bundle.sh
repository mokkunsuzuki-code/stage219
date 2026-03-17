#!/usr/bin/env bash
# MIT License © 2025 Motohiro Suzuki

set -euo pipefail

EVIDENCE_PATH="${1:-out/reports/summary.md}"
CLAIM_ID="${2:-A2}"
JOB_NAME="${3:-stage215_bundle}"
SIGNATURE_PATH="${4:-out/signatures/summary.sig}"
SHA256_PATH="${5:-out/reports/summary.sha256.txt}"
LOG_PATH="${6:-out/transparency/transparency_log.jsonl}"

mkdir -p out/transparency

if [ ! -f "$EVIDENCE_PATH" ]; then
  echo "[ERROR] evidence not found: $EVIDENCE_PATH"
  exit 1
fi

python3 tools/generate_transparency_log.py \
  --claim "$CLAIM_ID" \
  --job "$JOB_NAME" \
  --evidence "$EVIDENCE_PATH" \
  --signature "$SIGNATURE_PATH" \
  --sha256-file "$SHA256_PATH" \
  --log "$LOG_PATH"

python3 tools/verify_transparency_log.py --log "$LOG_PATH"

echo "[OK] Stage215 transparency bundle complete"
