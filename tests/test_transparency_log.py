# MIT License © 2025 Motohiro Suzuki

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_generate_and_verify_transparency_log(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("hello stage215\n", encoding="utf-8")

    signature = tmp_path / "evidence.sig"
    signature.write_text("dummy-signature\n", encoding="utf-8")

    sha256_file = tmp_path / "evidence.sha256.txt"
    sha256_file.write_text("placeholder-sha256\n", encoding="utf-8")

    log_path = tmp_path / "transparency_log.jsonl"

    subprocess.run(
        [
            sys.executable,
            "tools/generate_transparency_log.py",
            "--claim",
            "A2",
            "--job",
            "pytest_job",
            "--evidence",
            str(evidence),
            "--signature",
            str(signature),
            "--sha256-file",
            str(sha256_file),
            "--log",
            str(log_path),
        ],
        check=True,
    )

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["claim"] == "A2"
    assert entry["job"] == "pytest_job"
    assert entry["evidence_path"] == str(evidence)

    subprocess.run(
        [
            sys.executable,
            "tools/verify_transparency_log.py",
            "--log",
            str(log_path),
        ],
        check=True,
    )
