# Version 2.2 — Current engineering status

Updated: 2026-11-20

The authoritative instructions, phased plan, decision register, work log, test ledger, blockers, and next task are maintained in:
- [MASTER_PROJECT_NOTE_V2_2.md](MASTER_PROJECT_NOTE_V2_2.md)

## Active development baseline
- Repository: https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2
- Active working branch: `v2/integration-baseline-2026-11-20`
- Current verified commit: `8962eac6dd4c0d0ae75042ac20938791a672985b`
- Project/package version: `2.2.0`
- Previous repository remains a read-only reference. Do not edit it.

## Current observed automated verification
- GitHub Actions run: https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2/actions/runs/44806927292
- Linux + PostgreSQL 16: **343 passed, 16 warnings, 0 failures**.
- Windows runner / Python 3.11: **336 passed, 1 warning, 0 failures**.
- PowerShell syntax checks passed for `setup.ps1`, `start.ps1`, and `install_backup_tasks.ps1`.
- These are hosted CI results, not a real installation or acceptance run on the hotel's Windows computer.
- The software is not yet production-accepted. Use synthetic data only.

## Branch alignment warning
The current `main` branch contains later V2.1 UI/employee-code/AI-gateway commits, while the active V2.2 working branch contains the broader imported HR/payroll baseline and subsequent V2.2 hardening. The histories have diverged. Do not overwrite either line or perform a blind merge. Reconcile useful changes deliberately as recorded in the master project note.

## Release status
**IN DEVELOPMENT — NOT PRODUCTION READY.** Do not mark complete until the remaining acceptance and actual Windows install/backup/restore gates are closed.
