#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Write SHA256 for evidence bundle.")
    parser.add_argument(
        "--input",
        default="evidence_bundle/evidence_bundle.json",
        help="Input bundle JSON",
    )
    parser.add_argument(
        "--output",
        default="evidence_bundle/evidence_bundle.sha256",
        help="Output SHA256 text file",
    )
    args = parser.parse_args()

    in_path = Path(args.input).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(in_path)
    line = f"{digest}  {in_path.name}\n"
    out_path.write_text(line, encoding="utf-8")

    print(f"[OK] wrote sha256: {out_path}")
    print(f"[OK] sha256={digest}")


if __name__ == "__main__":
    main()
