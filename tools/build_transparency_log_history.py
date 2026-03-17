#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def discover_history_files(history_dir: Path) -> List[Path]:
    return sorted(history_dir.glob("checkpoint_*.json"))


def extract_next_sequence(history_files: List[Path]) -> int:
    max_seq = 0
    for p in history_files:
        stem = p.stem
        # checkpoint_0001
        try:
            seq = int(stem.split("_")[-1])
            if seq > max_seq:
                max_seq = seq
        except ValueError:
            continue
    return max_seq + 1


def compute_file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def collect_transparency_artifacts(transparency_dir: Path) -> List[Dict[str, str]]:
    artifacts: List[Dict[str, str]] = []

    candidates = [
        transparency_dir / "transparency_log.json",
        transparency_dir / "merkle_tree.json",
        transparency_dir / "root.txt",
        transparency_dir / "checkpoint.json",
    ]

    proofs_dir = transparency_dir / "inclusion_proofs"
    if proofs_dir.exists():
        for p in sorted(proofs_dir.glob("*")):
            if p.is_file():
                candidates.append(p)

    for p in candidates:
        if p.exists() and p.is_file():
            artifacts.append(
                {
                    "path": str(p.relative_to(transparency_dir.parent)),
                    "sha256": compute_file_digest(p),
                }
            )

    return artifacts


def load_or_init_index(index_path: Path, log_id: str) -> Dict[str, Any]:
    if index_path.exists():
        data = load_json(index_path)
        if "log_id" not in data:
            data["log_id"] = log_id
        if "checkpoints" not in data:
            data["checkpoints"] = []
        return data
    return {
        "log_id": log_id,
        "checkpoints": [],
    }


def try_sign_with_private_key(checkpoint_unsigned: Dict[str, Any], private_key_path: Optional[Path]) -> Dict[str, Optional[str]]:
    """
    Minimal placeholder signing approach:
    - If a private key file exists, derive a deterministic signature-like digest from:
      private_key_bytes + canonical_json(unsigned_checkpoint)
    This is NOT asymmetric crypto verification, but keeps structure aligned for now.
    - Can be replaced later with real RSA/Ed25519 signing.
    """
    if private_key_path is None or not private_key_path.exists():
        return {
            "signed_by": None,
            "signature_algorithm": None,
            "signature": None,
        }

    key_bytes = private_key_path.read_bytes()
    payload = canonical_json_bytes(checkpoint_unsigned)
    digest = hashlib.sha256(key_bytes + payload).digest()
    sig_b64 = base64.b64encode(digest).decode("ascii")

    return {
        "signed_by": private_key_path.name,
        "signature_algorithm": "sha256-keyed-placeholder",
        "signature": sig_b64,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build checkpoint history for append-only transparency log.")
    parser.add_argument("--transparency-dir", required=True, help="Path to out/transparency")
    parser.add_argument("--log-id", default="qsp-transparency-log", help="Logical transparency log identifier")
    parser.add_argument(
        "--private-key",
        default="keys/transparency_log_private.key",
        help="Optional private key path for placeholder signing",
    )
    args = parser.parse_args()

    transparency_dir = Path(args.transparency_dir).resolve()
    history_dir = transparency_dir / "history"
    index_path = transparency_dir / "checkpoint_index.json"
    checkpoint_path = transparency_dir / "checkpoint.json"
    merkle_tree_path = transparency_dir / "merkle_tree.json"

    if not transparency_dir.exists():
        raise SystemExit(f"[ERROR] transparency dir not found: {transparency_dir}")

    if not checkpoint_path.exists():
        raise SystemExit(f"[ERROR] checkpoint not found: {checkpoint_path}")

    if not merkle_tree_path.exists():
        raise SystemExit(f"[ERROR] merkle tree not found: {merkle_tree_path}")

    history_dir.mkdir(parents=True, exist_ok=True)

    merkle_tree = load_json(merkle_tree_path)
    checkpoint_current = load_json(checkpoint_path)

    history_files = discover_history_files(history_dir)
    next_sequence = extract_next_sequence(history_files)

    previous_checkpoint_hash = None
    previous_checkpoint_file = None
    if history_files:
        previous_checkpoint_file = history_files[-1].name
        previous_checkpoint_hash = compute_file_digest(history_files[-1])

    unsigned_checkpoint: Dict[str, Any] = {
        "log_id": args.log_id,
        "sequence": next_sequence,
        "sequence_label": f"{next_sequence:04d}",
        "timestamp": utc_now_iso(),
        "entry_count": checkpoint_current.get("entry_count"),
        "merkle_root": checkpoint_current.get("merkle_root"),
        "root_hash_algorithm": checkpoint_current.get("root_hash_algorithm", "sha256"),
        "checkpoint_source": "out/transparency/checkpoint.json",
        "previous_checkpoint_file": previous_checkpoint_file,
        "previous_checkpoint_hash": previous_checkpoint_hash,
        "artifacts": collect_transparency_artifacts(transparency_dir),
    }

    if "levels" in merkle_tree:
        unsigned_checkpoint["merkle_tree_levels"] = len(merkle_tree["levels"])
    if "leaf_count" in merkle_tree:
        unsigned_checkpoint["leaf_count"] = merkle_tree["leaf_count"]

    sig = try_sign_with_private_key(unsigned_checkpoint, Path(args.private_key))

    checkpoint_full: Dict[str, Any] = {
        **unsigned_checkpoint,
        "signed_by": sig["signed_by"],
        "signature_algorithm": sig["signature_algorithm"],
        "signature": sig["signature"],
    }

    checkpoint_hash = sha256_bytes(canonical_json_bytes(checkpoint_full))
    checkpoint_full["checkpoint_hash"] = checkpoint_hash

    history_file_name = f"checkpoint_{next_sequence:04d}.json"
    history_file_path = history_dir / history_file_name
    write_json(history_file_path, checkpoint_full)

    # latest checkpoint mirror
    write_json(checkpoint_path, checkpoint_full)

    index = load_or_init_index(index_path, args.log_id)
    if history_file_name not in index["checkpoints"]:
        index["checkpoints"].append(history_file_name)
    write_json(index_path, index)

    print(f"[OK] wrote history checkpoint: {history_file_path}")
    print(f"[OK] updated latest checkpoint: {checkpoint_path}")
    print(f"[OK] updated checkpoint index: {index_path}")
    print(f"[OK] log_id: {args.log_id}")
    print(f"[OK] sequence: {next_sequence:04d}")
    print(f"[OK] merkle_root: {checkpoint_full.get('merkle_root')}")
    print(f"[OK] entry_count: {checkpoint_full.get('entry_count')}")


if __name__ == "__main__":
    main()
