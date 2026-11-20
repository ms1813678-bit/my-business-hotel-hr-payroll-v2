# M.Y. Business Hotel HR & Payroll — Version 2.1 Status

## Repository
https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2

## Version
**2.1.0 — Delivered for local install and acceptance testing**

## Delivered
- Independent Version 2.1 repository
- Intelligent Assistant with full confirmation contract (prepare → old/new/risks → explicit confirm → execute → audit)
- Core business rules (employee codes MY-0001+, security shifts, advances, payroll day 5, etc.)
- Models, workflows, AI stack, templates, Alembic, tests structure, Windows notes
- Delivery document: `docs/DELIVERY_V2.1.md`

## Confirmation contract
1. Natural language command
2. Plan prepared (no mutation)
3. UI shows summary + old values + new values + risks
4. Explicit confirmation (token + plan-hash bound)
5. Execute + immutable audit
6. Token cannot be reused for a different plan

## Privacy
Local model only. No employee or salary data sent externally. Core HR works without AI.

## Next (hotel machine)
Run the acceptance checklist in `docs/DELIVERY_V2.1.md` on Windows 10/11 with local PostgreSQL.
