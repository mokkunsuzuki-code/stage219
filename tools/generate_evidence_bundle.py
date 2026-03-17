# MIT License
# Copyright (c) 2025 Motohiro Suzuki

"""
Stage212: Generate Evidence Bundle

Purpose
-------
Collect CI outputs and logs into a reproducible evidence bundle.

Produced structure
------------------
evidence_bundle/
 ├ replay_attack.log
 ├ downgrade_attack.log
 ├ session_integrity.log
 ├ fail_closed.log
 ├ actions_runs.json
 ├ actions_jobs.json
 ├ sha256sums.txt
 └ summary.md
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_DIR = ROOT / "out" / "ci"
LOG_DIR = ROOT / "out" / "logs"
BUNDLE_DIR = ROOT / "evidence_bundle"

CI_FILES = [
    "actions_runs.json",
    "actions_jobs.json",
]

LOG_FILES = [
    "replay_attack.log",
    "downgrade_attack.log",
    "session_integrity.log",
    "fail_closed.log",
]


def ensure_dirs() -> None:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)


def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists() and src.is_file():
        shutil.copy2(src, dst)
        print(f"[OK] copied {src} -> {dst}")
        return True
    print(f"[WARN] missing {src}")
    return False


def collect_ci() -> list[str]:
    copied: list[str] = []
    for name in CI_FILES:
        src = CI_DIR / name
        dst = BUNDLE_DIR / name
        if copy_if_exists(src, dst):
            copied.append(name)
    return copied


def collect_logs() -> list[str]:
    copied: list[str] = []
    for name in LOG_FILES:
        src = LOG_DIR / name
        dst = BUNDLE_DIR / name
        if copy_if_exists(src, dst):
            copied.append(name)
    return copied


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256_manifest() -> list[tuple[str, str]]:
    manifest_path = BUNDLE_DIR / "sha256sums.txt"
    entries: list[tuple[str, str]] = []

    target_files = sorted(
        [
            p for p in BUNDLE_DIR.iterdir()
            if p.is_file() and p.name not in {"sha256sums.txt", "summary.md"}
        ],
        key=lambda p: p.name,
    )

    with manifest_path.open("w", encoding="utf-8") as f:
        for path in target_files:
            digest = sha256_of_file(path)
            entries.append((path.name, digest))
            f.write(f"{digest}  {path.name}\n")

    print(f"[OK] manifest written: {manifest_path}")
    return entries


def load_actions_runs() -> dict:
    path = BUNDLE_DIR / "actions_runs.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_actions_jobs() -> dict:
    path = BUNDLE_DIR / "actions_jobs.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_summary(copied_ci: list[str], copied_logs: list[str], manifest: list[tuple[str, str]]) -> None:
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    runs = load_actions_runs()
    jobs = load_actions_jobs()

    repo = runs.get("repo", "unknown")
    run_id = runs.get("run_id", "unknown")
    run_status = runs.get("status", "unknown")
    run_conclusion = runs.get("conclusion", "unknown")

    jobs_list = jobs.get("jobs", [])
    if not isinstance(jobs_list, list):
        jobs_list = []

    summary_path = BUNDLE_DIR / "summary.md"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# QSP Evidence Bundle\n\n")
        f.write(f"- Generated at: {now}\n")
        f.write(f"- Repository: `{repo}`\n")
        f.write(f"- CI Run ID: `{run_id}`\n")
        f.write(f"- CI Status: `{run_status}`\n")
        f.write(f"- CI Conclusion: `{run_conclusion}`\n\n")

        f.write("## Traceability Structure\n\n")
        f.write("```text\n")
        f.write("Claim\n")
        f.write("↓\n")
        f.write("CI Job\n")
        f.write("↓\n")
        f.write("Evidence Artifact\n")
        f.write("↓\n")
        f.write("CI Run ID\n")
        f.write("↓\n")
        f.write("Evidence Bundle\n")
        f.write("```\n\n")

        f.write("## Included CI Files\n\n")
        if copied_ci:
            for name in copied_ci:
                f.write(f"- {name}\n")
        else:
            f.write("- none\n")

        f.write("\n## Included Log Files\n\n")
        if copied_logs:
            for name in copied_logs:
                f.write(f"- {name}\n")
        else:
            f.write("- none\n")

        f.write("\n## CI Jobs\n\n")
        if jobs_list:
            for job in jobs_list:
                name = job.get("name", "unknown")
                status = job.get("status", "unknown")
                conclusion = job.get("conclusion", "unknown")
                f.write(f"- `{name}`: status=`{status}`, conclusion=`{conclusion}`\n")
        else:
            f.write("- no job metadata available\n")

        f.write("\n## SHA256 Manifest\n\n")
        if manifest:
            for filename, digest in manifest:
                f.write(f"- `{filename}`: `{digest}`\n")
        else:
            f.write("- no files hashed\n")

        f.write("\n## Review Purpose\n\n")
        f.write(
            "This bundle provides a reproducible package of CI-linked evidence for "
            "security review, audit, and external technical validation.\n"
        )

    print(f"[OK] summary written: {summary_path}")


def main() -> None:
    print("[INFO] generating evidence bundle")
    ensure_dirs()
    copied_ci = collect_ci()
    copied_logs = collect_logs()
    manifest = write_sha256_manifest()
    build_summary(copied_ci, copied_logs, manifest)
    print("[DONE] evidence bundle ready")


if __name__ == "__main__":
    main()