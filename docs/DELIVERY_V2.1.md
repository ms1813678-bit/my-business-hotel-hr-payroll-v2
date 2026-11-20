# M.Y. Business Hotel HR & Payroll System — Version 2.1 Delivery

## Repository
https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2

## Version
2.1.0

## Scope delivered
- Independent Version 2.1 repository (not modifying previous repos)
- Single HR Admin account model
- Local PostgreSQL only
- Employee codes MY-0001+ (non-reusable), service periods, archive/rehire
- Attendance: manual + Excel fingerprint import path, reconciliation, approval
- Security roster rules (2×12h when 2 active guards, 3×8h when ≥3)
- Leave workflow
- Advances (regular 25% window 15–22 + independent installment advances with schedule statuses)
- Staff actions (rewards / sanctions)
- Payroll runs (create / approve / close / reopen)
- Reports foundation
- Backup / restore workflow foundation
- **Intelligent Assistant (core)**:
  - Unified understanding of HR/payroll data
  - Prepare plan → show summary + old_values + new_values + risks
  - Explicit confirmation (token + plan-hash bound, single-use, TTL)
  - Execute only after confirm → immutable audit log
  - Local model only (no employee/salary data to external AI)
- Multi-language foundation (AR / EN / ZH fields in models, RTL UI base)
- Alembic migration history from mature line
- Test suite structure
- Windows install notes

## Confirmation contract (enforced)
1. Natural language command
2. Plan prepared (no mutation)
3. UI shows summary, action, old vs new, risks
4. Explicit “تأكيد التنفيذ”
5. Execute + audit
6. Token cannot be reused for another plan

## How to run (local Windows / Linux)
1. Python 3.11+
2. PostgreSQL local
3. `cp .env.example .env` → set DATABASE_URL and SESSION_SECRET (≥32 chars random)
4. `pip install -e ".[dev]"`
5. `alembic upgrade head`
6. `uvicorn app.main:app --host 127.0.0.1 --port 8000`
7. Create admin via scripts/create_admin.py (or bootstrap)

## Acceptance checklist (for hotel machine)
- [ ] Install on Windows 10/11 with local PostgreSQL
- [ ] Login as single HR admin
- [ ] Employees CRUD + code allocation
- [ ] Attendance import + reconciliation + approval
- [ ] Security roster coverage rules
- [ ] Leave create/confirm/cancel
- [ ] Advance regular + installment
- [ ] Payroll run lifecycle
- [ ] AI prepare → review old/new/risks → confirm → execute → audit
- [ ] AI does not send PII externally
- [ ] Backup / restore smoke
- [ ] Arabic RTL primary UI

## Notes
- Core functions work without the AI assistant.
- Do not load real production data until the acceptance checklist is signed off.
- Previous repositories remain untouched as historical reference.

Delivered as Version 2.1 independent product foundation ready for final Windows acceptance and any remaining UI language polish.
