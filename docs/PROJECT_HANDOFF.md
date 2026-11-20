# Project handoff and current decisions

## Current integration branch
- Branch: feature/bilingual-ui-rtl-ltr
- Source baseline: main at daeed7a50e272cf155e4797bca07c84276afa237
- Target branch: main
- This is the controlled final-acceptance track. Do not merge it to main until all acceptance gates are green and the owner explicitly approves the merge.

## Confirmed business decisions
1. Reports are manual only.
2. Regular monthly advances alone are limited to 25% of basic salary.
3. Installment/large advances are independent of the 25% limit and may use 1–36 installments.
4. Advance installment accounting starts in the request month; payout date is the 5th of the following month.
5. Payroll advance deductions consume the installment ledger, never the full advance amount. Closing applies installments; reopening reverses them.
6. Positive overtime requires explicit administrator approval.
7. Security attendance requires at least two active guards every day. Exactly two guards use 12-hour coverage; three or more use 8-hour coverage.
8. Attendance remains evidence-first: source files are retained, daily records require HR approval, and monthly approval requires both source imports and explicit coverage confirmation.
9. Employee codes are never reused. Rehire preserves the code but creates a new service period.

## Latest automated verification after local-database security guard (2026-11-20)
- Branch: `feature/bilingual-ui-rtl-ltr`.
- Verified commit: `eb027b46776461c4c1dc8e6bfea1199da083408a`.
- GitHub Actions run: [44737576171](https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-system/actions/runs/44737576171) — completed successfully.
- Linux + PostgreSQL 16: 330 passed, 16 warnings, zero failures.
- Windows runner: 323 passed, 1 warning, zero failures.
- PowerShell syntax checks: `setup.ps1`, `start.ps1`, `install_backup_tasks.ps1` passed.
- Added application-level and Windows setup validation to reject remote PostgreSQL hosts; only localhost, 127.0.0.1, and ::1 are accepted.
- This proves CI compatibility only. It does not replace installation and backup/restore acceptance on the hotel PC.

## Final acceptance gates
1. Full automated test suite passes on the final-acceptance branch, including PostgreSQL migration/concurrency tests.
2. Windows runner installation/compatibility passes.
3. Real Windows 10 or Windows 11 + PostgreSQL installation is executed on the hotel target PC.
4. Backup creation, integrity validation, restore, and rollback behavior are executed against the target PostgreSQL environment and backup drive.
5. Synthetic end-to-end business flow passes: employee/service period -> attendance -> security roster -> leave -> advance/installment ledger -> sanctions/rewards -> payroll -> payment -> reports -> backup/restore.
6. AI assistant approval-gate tests pass and the application remains usable with local AI unavailable.
7. Arabic/English/Simplified Chinese translations and RTL/LTR UI regression are checked.
8. Only after all gates pass may `feature/bilingual-ui-rtl-ltr` be merged to `main` with explicit owner approval.

## Repository hygiene verification
- The new repository contains no tracked `.env`, database, spreadsheet, PDF, backup archive, private key, local data, or `var/` files.
- `.gitignore` excludes `.env`, `data/`, `backups/`, `var/`, virtual environments, build output, caches, logs, and temporary files.
- The stale `.github/workflows/release-ci.yml` file and old `tests/test_monthly_report_schedule.py` name were removed from this repository; the manual-report CLI test remains under `tests/test_manual_report_cli.py`.
- The old repository was left unchanged as the historical source; no source files were removed from it.

## Verification notes
- PostgreSQL migration tests are in tests/test_postgres_migrations.py.
- No production data should be entered before final acceptance.
- main remains unchanged by this acceptance track.
