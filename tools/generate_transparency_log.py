#!/usr/bin/env python3
# MIT License © 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_text_if_exists(path: Path) -> str | None:
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return None


def count_existing_entries(log_path: Path) -> int:
    if not log_path.exists():
        return 0
    with log_path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append evidence metadata to a transparency log (JSONL)."
    )
    parser.add_argument("--claim", required=True, help="Claim ID, e.g. A2")
    parser.add_argument("--job", required=True, help="CI job name")
    parser.add_argument("--evidence", required=True, help="Path to evidence artifact")
    parser.add_argument("--signature", required=False, help="Path to signature file")
    parser.add_argument("--sha256-file", required=False, help="Path to sha256 text file")
    parser.add_argument(
        "--log",
        default="out/transparency/transparency_log.jsonl",
        help="Path to append-only transparency log",
    )
    args = parser.parse_args()

    evidence_path = Path(args.evidence)
    signature_path = Path(args.signature) if args.signature else None
    sha256_file_path = Path(args.sha256_file) if args.sha256_file else None
    log_path = Path(args.log)

    if not evidence_path.exists():
        raise SystemExit(f"[ERROR] evidence not found: {evidence_path}")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    evidence_hash = sha256_file(evidence_path)
    signature_hash = sha256_file(signature_path) if signature_path and signature_path.exists() else None
    sha256_declared = load_text_if_exists(sha256_file_path) if sha256_file_path else None

    entry_index = count_existing_entries(log_path) + 1

    entry = {
        "log_index": entry_index,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "claim": args.claim,
        "job": args.job,
        "evidence_path": str(evidence_path),
        "evidence_sha256": evidence_hash,
        "signature_path": str(signature_path) if signature_path else None,
        "signature_sha256": signature_hash,
        "sha256_file_path": str(sha256_file_path) if sha256_file_path else None,
        "sha256_file_text": sha256_declared,
        "append_only_note": "Entries are append-only; previous entries must not be modified.",
    }

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    latest_path = log_path.parent / "latest_entry.json"
    latest_path.write_text(
        json.dumps(entry, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[OK] appended transparency log entry #{entry_index}")
    print(f"[OK] log: {log_path}")
    print(f"[OK] latest entry: {latest_path}")


if __name__ == "__main__":
    main()
