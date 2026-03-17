#!/usr/bin/env python3
# MIT License © 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify append-only transparency log entries against evidence files."
    )
    parser.add_argument(
        "--log",
        default="out/transparency/transparency_log.jsonl",
        help="Path to transparency log JSONL",
    )
    args = parser.parse_args()

    log_path = Path(args.log)

    if not log_path.exists():
        raise SystemExit(f"[ERROR] log not found: {log_path}")

    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise SystemExit("[ERROR] transparency log is empty")

    previous_index = 0

    for i, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"[ERROR] invalid JSON on line {i}: {e}")

        log_index = entry.get("log_index")
        if log_index != previous_index + 1:
            raise SystemExit(
                f"[ERROR] non-sequential log_index at line {i}: expected {previous_index + 1}, got {log_index}"
            )
        previous_index = log_index

        evidence_path = Path(entry["evidence_path"])
        if not evidence_path.exists():
            raise SystemExit(f"[ERROR] missing evidence file at line {i}: {evidence_path}")

        actual_evidence_hash = sha256_file(evidence_path)
        if actual_evidence_hash != entry["evidence_sha256"]:
            raise SystemExit(
                f"[ERROR] evidence hash mismatch at line {i}: "
                f"expected {entry['evidence_sha256']}, got {actual_evidence_hash}"
            )

        signature_path_value = entry.get("signature_path")
        signature_hash_value = entry.get("signature_sha256")
        if signature_path_value and signature_hash_value:
            signature_path = Path(signature_path_value)
            if not signature_path.exists():
                raise SystemExit(f"[ERROR] missing signature file at line {i}: {signature_path}")
            actual_signature_hash = sha256_file(signature_path)
            if actual_signature_hash != signature_hash_value:
                raise SystemExit(
                    f"[ERROR] signature hash mismatch at line {i}: "
                    f"expected {signature_hash_value}, got {actual_signature_hash}"
                )

    print(f"[OK] transparency log verified: {log_path}")
    print(f"[OK] entries: {len(lines)}")


if __name__ == "__main__":
    main()
