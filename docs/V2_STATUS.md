# M.Y. Business Hotel HR & Payroll — Version 2.1 Status

## Repository
https://github.com/ms1813678-bit/my-business-hotel-hr-payroll-v2

## Goal
Independent, production-oriented **Version 2.1** with:
- Unified executive intelligent assistant (prepare → show old/new → explicit confirm → execute → audit)
- Full Arabic / English / Simplified Chinese
- Local PostgreSQL only
- All hotel business rules preserved
- Single HR Admin account

## What is in this repository (current)
- Full models (employees, service periods, attendance, leave, advances + installments, staff actions, payroll runs, security roster, audit, backup)
- Complete AI stack: ai_assistant (local Ollama-compatible), ai_agent (allowlisted actions), ai_gateway (token-bound confirmation), ai_hr_queries
- Workflows: attendance (manual + Excel import + reconciliation + approval), leave, advances, staff actions (rewards/sanctions), payroll (create/approve/close/reopen), security roster (2×12h / 3×8h rules), backup/restore, reports
- Server-side templates for all major screens
- Alembic migrations history
- Unit and integration tests suite
- Windows install notes and scripts

## Confirmation flow (required behaviour)
1. Admin writes natural language command.
2. Assistant builds a plan (no DB mutation yet).
3. System shows:
   - Summary in Arabic (and UI language)
   - Action type
   - Old values vs new values when modifying
   - Potential risks
4. Admin must click explicit confirmation (token-bound to that exact plan).
5. Only then execute + write immutable audit log.
6. Previous confirmation tokens cannot be reused for a different plan.

## Privacy
No employee or salary data is ever sent to external AI services. Local model only (loopback). Core HR functions work without the assistant.

## Version
2.1.0

## Next hardening (in progress)
- Multi-language UI strings (AR / EN / ZH) fully wired
- Proactive issue detection surface on dashboard
- Final Windows packaging polish
- End-to-end acceptance run on Windows 10/11 target
