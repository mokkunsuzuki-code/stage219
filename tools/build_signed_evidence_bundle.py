#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(repo_root: Path, patterns: Iterable[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        for p in repo_root.glob(pattern):
            if p.is_file():
                found.append(p)
    unique_sorted = sorted(set(found))
    return unique_sorted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a signed-evidence-ready bundle from Stage212 artifacts."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--out-json",
        default="evidence_bundle/evidence_bundle.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_json = (repo_root / args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)

    patterns = [
        "claims/*.yaml",
        "claims/*.yml",
        "claims/*.json",
        "claims/*.md",
        "out/ci/*.json",
        "out/reports/*.md",
        "out/reports/*.json",
        "out/formal/*.txt",
        "out/formal/*.json",
        "out/formal/*.md",
        "docs/*.md",
        "README.md",
    ]

    files = collect_files(repo_root, patterns)

    artifacts = []
    for path in files:
        rel = path.relative_to(repo_root).as_posix()
        artifacts.append(
            {
                "path": rel,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )

    bundle = {
        "bundle_type": "signed_evidence_bundle",
        "stage": "Stage213",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": repo_root.name,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "notes": [
            "This bundle is intended to bind claim-related evidence to cryptographic integrity metadata.",
            "Bundle JSON itself is later hashed and signed.",
        ],
    }

    out_json.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] wrote bundle: {out_json}")
    print(f"[OK] artifact_count: {len(artifacts)}")


if __name__ == "__main__":
    main()
