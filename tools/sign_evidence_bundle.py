#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Motohiro Suzuki

from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sign evidence bundle with OpenSSL private key.")
    parser.add_argument(
        "--bundle",
        default="evidence_bundle/evidence_bundle.json",
        help="Bundle JSON file",
    )
    parser.add_argument(
        "--private-key",
        default="keys/evidence_signing_private.pem",
        help="PEM private key path",
    )
    parser.add_argument(
        "--signature-bin",
        default="signatures/evidence_bundle.sig",
        help="Binary signature output path",
    )
    parser.add_argument(
        "--signature-json",
        default="signatures/evidence_bundle.signature.json",
        help="JSON metadata output path",
    )
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    private_key = Path(args.private_key).resolve()
    signature_bin = Path(args.signature_bin).resolve()
    signature_json = Path(args.signature_json).resolve()

    signature_bin.parent.mkdir(parents=True, exist_ok=True)
    signature_json.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            "openssl",
            "dgst",
            "-sha256",
            "-sign",
            str(private_key),
            "-out",
            str(signature_bin),
            str(bundle),
        ]
    )

    sig_b64 = base64.b64encode(signature_bin.read_bytes()).decode("ascii")

    metadata = {
        "bundle_path": bundle.name,
        "signature_path": signature_bin.name,
        "algorithm": "RSA-SHA256",
        "signature_base64": sig_b64,
    }

    signature_json.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] wrote binary signature: {signature_bin}")
    print(f"[OK] wrote signature metadata: {signature_json}")


if __name__ == "__main__":
    main()
