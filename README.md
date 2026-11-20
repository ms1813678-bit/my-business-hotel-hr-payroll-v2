# M.Y. Business Hotel — HR & Payroll System — Version 2

**Independent Version 2.2 | M.Y. Business Hotel — Maadi, Cairo**

A local-first HR and payroll application for Windows 10/11, using PostgreSQL on the hotel computer. Version 2 is developed in this repository only. The previous repository is a read-only reference and must not be modified as part of V2 work.

## Product commitments

- One account only: HR Manager / System Administrator.
- Arabic (RTL), English (LTR), and Simplified Chinese (LTR).
- Local PostgreSQL and local file storage. No cloud runtime.
- Core HR/payroll workflows continue when the local AI model is unavailable.
- The intelligent assistant is a first-class system component: cross-module read/analysis, proactive checks, and controlled execution.
- Every write command follows prepare → show exact changes/risks → explicit operation-bound confirmation → execute → audit.
- No employee portal, manager/supervisor accounts, mobile attendance, GPS, inventory, or purchasing module.

## Hotel rules

- Employee codes start at MY-0001 and are never reused. Rehire retains the same employee code and creates a new service period.
- Attendance is entered manually or imported from fingerprint Excel; discrepancies are reviewed before approval.
- Security shift model is determined by the count of active guards assigned to work: exactly two use 08:00–20:00 and 20:00–08:00; three or more use configured 8-hour shifts. Never fewer than two assigned to work, no gaps, no overlap. Overnight shifts belong to their start date.
- Regular advances: request window 15–22 and maximum 25% of eligible basic salary for the accounting month. Installment advances are separate, 1–36 installments.
- Payroll is normally paid on day 5 of the following month. Hourly rate = basic salary ÷ (daily hours × 30). Absence uses actual calendar days; partial first month is prorated by actual calendar days.
- Overtime requires HR approval. Taxes and insurance are manually entered/approved; no guessed rates.
- Bonuses and sanctions are manually entered; no automatically generated amounts.

## Architecture

- Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16.
- Server-rendered admin UI with local static assets.
- Ollama-compatible local model on loopback only; no employee or payroll information is sent to external AI services.
- Single-use, expiring, actor-bound, plan-hash-bound confirmation tokens and audit history.
- Windows PowerShell setup/start and local backup/restore scripts.

## Development status

The initial V2 repository was a small foundation. The current integration branch imports the broader HR/payroll implementation and tests from the latest reviewed source branch as a starting baseline. This is not a production release. The imported test suite and Windows installation must be rerun on the V2 commit; no test is claimed successful until its result is observed.

Use synthetic data only until all V2 acceptance checks pass. See:
- `docs/PROJECT_SPEC.md`
- `docs/AI_ASSISTANT_ARCHITECTURE.md`
- `docs/ACCEPTANCE_CHECKLIST_AR.md`
- `docs/WINDOWS_INSTALL.md`

## Local development

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
# Configure a local PostgreSQL DATABASE_URL and a unique SESSION_SECRET.
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Do not commit `.env`, credentials, database dumps, or real employee data.
