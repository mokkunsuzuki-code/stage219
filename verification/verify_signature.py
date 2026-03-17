#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify signed evidence bundle.")
    parser.add_argument(
        "--bundle",
        default="evidence_bundle/evidence_bundle.json",
        help="Bundle JSON file",
    )
    parser.add_argument(
        "--public-key",
        default="keys/evidence_signing_public.pem",
        help="PEM public key path",
    )
    parser.add_argument(
        "--signature",
        default="signatures/evidence_bundle.sig",
        help="Binary signature file",
    )
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    public_key = Path(args.public_key).resolve()
    signature = Path(args.signature).resolve()

    cmd = [
        "openssl",
        "dgst",
        "-sha256",
        "-verify",
        str(public_key),
        "-signature",
        str(signature),
        str(bundle),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True)

    if completed.returncode == 0:
        print("[OK] signature verification passed")
        if completed.stdout.strip():
            print(completed.stdout.strip())
        sys.exit(0)

    print("[ERROR] signature verification failed")
    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.stderr.strip():
        print(completed.stderr.strip())
    sys.exit(1)


if __name__ == "__main__":
    main()
