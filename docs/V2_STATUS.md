# M.Y. Business Hotel HR & Payroll — Version 2 Status

## Repository
https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2

## Goal
Independent, production-oriented Version 2 with:
- Unified executive intelligent assistant (prepare → show old/new → explicit confirm → execute → audit)
- Full Arabic / English / Simplified Chinese
- Local PostgreSQL only
- All hotel business rules preserved
- Single HR Admin account

## What is already in this repository
- Project foundation (pyproject 2.0.0, config, db, security, auth, CSRF, employee codes, payroll math)
- Local AI assistant (Ollama-compatible, loopback only)
- Leave workflow (create / confirm / cancel / balance adjustments)
- Advance repayment schedule helpers
- Annotated confirmation gateway design

## Next commits (in progress, no pause)
1. Full models.py
2. Full ai_agent.py + enhanced prepare summary (old vs new values)
3. Full ai_gateway.py
4. Attendance, payroll, security roster workflows
5. Templates + multi-language shell
6. Alembic migrations
7. Windows install scripts
8. Tests

## Confirmation flow (required behaviour)
1. Admin writes natural language command.
2. Assistant builds a plan (no DB mutation yet).
3. System shows:
   - Summary in Arabic
   - Action type
   - Old values vs new values
   - Potential risks
4. Admin must click explicit "تأكيد التنفيذ" (token-bound).
5. Only then execute + write immutable audit log.
6. Previous confirmation tokens cannot be reused for a different plan.

## Privacy
No employee or salary data is ever sent to external AI services.
