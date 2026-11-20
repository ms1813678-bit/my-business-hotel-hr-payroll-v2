# Version 2.2 — Current engineering status

Updated: 2026-11-20

The authoritative instructions, phased plan, decisions, work log, test ledger, blockers, and next task are maintained in:
- [MASTER_PROJECT_NOTE_V2_2.md](MASTER_PROJECT_NOTE_V2_2.md)

## Active development baseline
- Repository: https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2
- Active working branch: `v2/integration-baseline-2026-11-20`
- Current commit: `b96505ecaa7f898709dc5a94f11ecf8419b3787e`
- Package version: `2.2.0`
- Previous repository: read-only reference; do not edit it.

## Recent work
- Selective branch comparison completed; see [BRANCH_INTEGRATION_MATRIX_V2_2.md](BRANCH_INTEGRATION_MATRIX_V2_2.md).
- AI confirmation screen is being aligned to V2.2 routes and locale handling.
- CI exposed two missing translations and a missing PostgreSQL migration for local AI conversation history.
- Fix commit: `b96505ecaa7f898709dc5a94f11ecf8419b3787e`; run [44809835813](https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2/actions/runs/44809835813) was in progress at update time.

## Last completed CI
- Commit: `5cdf6c84efa5b3fa91cd73e057607f1a8496f9fd`
- Linux + PostgreSQL 16: 343 passed, 16 warnings, 0 failures.
- Windows runner / Python 3.11: 336 passed, 1 warning, 0 failures.
- The later AI UI commit failed four tests; fixes have been committed and are pending CI verification.

## Not production-ready
Hosted CI is not a real installation test on the hotel's Windows 10/11 computer. Local install, backup/restore, and acceptance workflow remain open. Use synthetic data only.
