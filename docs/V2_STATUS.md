# Version 2 — Engineering status

Updated: 2026-11-20

## Repository and isolation
- Repository: https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2
- Integration branch: `v2/integration-baseline-2026-11-20`
- Previous source repository is reference-only; no writes are made there.
- Imported baseline source: `ms1813678-bit/my-business-hotel-hr-payroll-system`, branch `feature/bilingual-ui-rtl-ltr`, commit `2f1d26bf81e9e3c68fe26103f1f2718be84facce`.
- Imported application, migrations, workflows, UI templates, Windows scripts, and tests as a starting baseline. The V2 README and this status document remain V2-specific.

## Important status qualification
This is an integration baseline, not a completed or production-accepted Version 2. The code has not yet been installed or executed on the hotel's Windows computer. CI must run against this V2 branch and the results must be inspected.

## Confirmed source capabilities found during review
- One administrator authentication, session security, CSRF, audit history.
- Employee lifecycle, non-reusable codes, service periods and change history.
- Attendance imports, source retention, reconciliation, review and approval.
- Security roster import/review and coverage checks.
- Leave balance transaction history.
- Regular and installment advances with payroll linkage.
- Manual rewards/sanctions, payroll runs, overtime approval, payment ledger, close/reopen.
- Local reports, backup/restore workflows, Windows setup scripts.
- Local-only AI assistant with a token-bound approval gateway and HR query module.
- Arabic/English/Simplified Chinese translation catalog and RTL/LTR direction handling in the imported UI baseline.

## V2 work still required
1. Run CI on this repository and repair any import/integration regressions.
2. Review every model, migration, route and business rule against the V2 brief.
3. Expand the assistant's cross-module read tools and complete missing write operations (including safe deletion/cancellation where valid).
4. Validate old/new preview values against the actual database immediately before confirmation; reject stale or altered plans.
5. Confirm assistant writes all use existing domain workflows and have complete audit records.
6. Add/verify Chinese translation coverage across all pages and forms.
7. Verify the exact security roster rule: count active registered guards, not daily attendance count; minimum two assigned to work and complete 24-hour coverage.
8. Verify advances, payroll snapshots, installment apply/reverse/cancel lifecycle and reopening.
9. Verify local backup/restore and Windows 10/11 setup on a real test machine.
10. Complete the Arabic acceptance checklist with synthetic data and record every unrun test honestly.

## Safety
- Never use real employee/payroll data before owner acceptance.
- Never send employee or payroll data to a remote model or service.
- No sensitive mutation without explicit, single-use confirmation by the HR administrator.
- No cloud hosting, inventory, purchasing, employee accounts, GPS or employee attendance app.
