# QSP Evidence Bundle

- Generated at: 2026-03-11T07:45:59Z
- Repository: `mokkunsuzuki-code/stage212`
- CI Run ID: `212001`
- CI Status: `completed`
- CI Conclusion: `success`

## Traceability Structure

```text
Claim
↓
CI Job
↓
Evidence Artifact
↓
CI Run ID
↓
Evidence Bundle
```

## Included CI Files

- actions_runs.json
- actions_jobs.json

## Included Log Files

- replay_attack.log
- downgrade_attack.log
- session_integrity.log
- fail_closed.log

## CI Jobs

- `attack_replay`: status=`completed`, conclusion=`success`
- `attack_downgrade`: status=`completed`, conclusion=`success`
- `session_integrity`: status=`completed`, conclusion=`success`
- `fail_closed`: status=`completed`, conclusion=`success`

## SHA256 Manifest

- `actions_jobs.json`: `89c5744a97ac1d4d9b3ee49c5a8837c8f59ec86e5a7c08e1bcf4c1dc30476b8f`
- `actions_runs.json`: `ce670be8e6140b8e9f8a4fe117a221f21291bf0f384f97b62319cf10dca2e186`
- `downgrade_attack.log`: `aa6f08a11b8f8886bac4cd75cc4b43c0629891dc75b29fe65bd40e26bad9a01e`
- `fail_closed.log`: `2387eb154c83251adabb01e912648608b3c9c78e47d9e68e696da7ed80dd28ac`
- `replay_attack.log`: `321f1023e672283823e99b696dd9d587ee00b6f712674d0ce963c89647fe3faf`
- `session_integrity.log`: `85eddd7eec4361f9c688c13180a5920365538fb8d6df0809b54c24f0749a1ff6`

## Review Purpose

This bundle provides a reproducible package of CI-linked evidence for security review, audit, and external technical validation.
