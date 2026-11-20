# M.Y. Business Hotel — HR & Payroll System — Version 2.1

**Local-first HR & Payroll system for M.Y. Business Hotel (Maadi, Cairo)**

Version 2.1 is an independent release focused on completeness, a powerful local intelligent assistant, multi-language support (Arabic / English / Simplified Chinese), and production readiness on Windows 10/11 with local PostgreSQL.

## Core principles

- **Single administrator** (HR Manager / System Admin). No employee self-service portals.
- **Local only**: PostgreSQL on the hotel machine. No cloud dependency for core functions.
- **Intelligent Assistant is central**: unified understanding of all HR/payroll data, ability to propose and (after explicit confirmation) execute create / update / delete / workflow actions, proactive issue detection, full audit trail.
- **Business rules preserved**: employee codes MY-0001+, non-reusable codes, security shift models (2×12h or 3×8h based on active guards), advances (25% regular window 15–22, independent installment advances), payroll on day 5, etc.
- **Languages**: Arabic (RTL), English (LTR), Simplified Chinese (LTR).

## Status

Version 2.1 foundation is complete on this repository: full data models, all core workflows, AI confirmation gateway, attendance/security/leave/advances/payroll/reports/backup, and test suite.

Do not use real employee or payroll data until the final acceptance checklist is passed and signed off.

## Architecture (high level)

- FastAPI + SQLAlchemy + Alembic + PostgreSQL
- Server-side rendered templates with modern admin UI
- Local optional LLM for the assistant (no employee/salary data sent externally)
- Explicit confirmation gateway for any mutating AI action
- Immutable audit log

## Key modules

- Employees (codes, service periods, archive/rehire, change history)
- Attendance (manual + Excel fingerprint import, reconciliation, approval)
- Security roster & shift coverage rules
- Leave management
- Advances & installment ledger
- Sanctions / rewards
- Payroll runs (approve / close / reopen)
- Reports (Excel / PDF)
- Backup & restore
- Intelligent Assistant (read + confirmed write)

## Development

```bash
# Python 3.11+
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# set DATABASE_URL and SESSION_SECRET (long random)
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

See `docs/` for PROJECT_SPEC, Windows install notes, and assistant design.

## License / ownership

Internal system for M.Y. Business Hotel. Not for public redistribution of real data.
