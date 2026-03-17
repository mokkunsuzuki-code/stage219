#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

TRANSPARENCY_DIR="out/transparency"

mkdir -p "$TRANSPARENCY_DIR/history"
mkdir -p "$TRANSPARENCY_DIR/inclusion_proofs"
mkdir -p keys

# placeholder key for deterministic signing structure
if [ ! -f "keys/transparency_log_private.key" ]; then
  echo "stage219-transparency-history-placeholder-key" > "keys/transparency_log_private.key"
fi

# If Stage218 builder exists, run it first.
if [ -x "./tools/run_stage218_checkpoint.sh" ]; then
  ./tools/run_stage218_checkpoint.sh
elif [ -f "./tools/build_transparency_log.py" ]; then
  python3 ./tools/build_transparency_log.py --input-dir out --output-dir "$TRANSPARENCY_DIR"
else
  echo "[WARN] Stage218 builder not found. Expecting existing files under $TRANSPARENCY_DIR"
fi

python3 ./tools/build_transparency_log_history.py \
  --transparency-dir "$TRANSPARENCY_DIR" \
  --log-id "qsp-transparency-log" \
  --private-key "keys/transparency_log_private.key"

echo "[OK] Stage219 history build complete"
echo
find "$TRANSPARENCY_DIR" -maxdepth 3 -type f | sort
