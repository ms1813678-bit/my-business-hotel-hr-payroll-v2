# V2 intelligent assistant — implementation contract

## Product role
The assistant is a first-class HR/payroll control surface, not a free-form chatbot. It must understand the whole local system and may read, analyze, prepare, and execute approved business operations.

## Privacy boundary
- The language model endpoint must be loopback-only (Ollama-compatible).
- The model never receives direct database, shell, filesystem, or arbitrary network tools.
- The application gathers only the minimum local context required for a question or a proposed operation.
- HR/payroll functions must remain available when the local model is stopped.

## Required write lifecycle
1. Parse the administrator's natural-language request.
2. Resolve target employees and records using exact registered identifiers; never invent IDs.
3. Build a typed, validated operation plan without mutating business data.
4. Read the current database values and produce a human-readable old/new diff, impact summary, and risks.
5. Persist an expiring, single-use approval token bound to the administrator and canonical plan hash.
6. Require a separate explicit confirmation action.
7. Re-read and validate target records and business invariants immediately before execution.
8. Execute only an allowlisted domain workflow in a database transaction.
9. Record actor, time, operation, target, before/after values, reason, approval reference, and result.
10. Return a clear execution result; never imply success before commit.

Changing any field, target, amount, date, or operation invalidates the previous confirmation. Expired, rejected, consumed, failed, or mismatched tokens cannot be reused.

## Financial and historical records
- Never hard-delete payroll history, payment records, audit records, employee service history, or applied installment history in a way that breaks the ledger.
- Use reversal, cancellation, correction entries, or archival for historical/financial records.
- A hard delete may be offered only for a record that is not referenced by an immutable or financial history and only when its domain workflow explicitly permits it.
- Employee archival preserves the employee code and all prior service/payroll records. Rehire starts another service period under the same code.

## Assistant coverage
Read/query: employees and service periods, attendance/import issues, security roster coverage, leave and balances, advances/installments, rewards/sanctions, payroll runs/items/payments, reports, and audit history.

Write: employee create/edit/transfer/archive/rehire; manual attendance; leave create/confirm/cancel/balance correction; advances and installments; rewards/sanctions; attendance approvals; payroll preparation and approved changes; safe cancellation/reversal and permitted deletions.

Proactive checks: payroll inconsistencies, attendance conflicts, missing source files, incomplete coverage, duplicate identities/events, unapplied/duplicate installments, leave-balance anomalies, and missing employee data.

## Current implementation note
The imported baseline has a structured agent and approval gateway, but the allowlist and executor do not yet cover every operation listed above. The work is incomplete until the implementation and tests prove each operation. Do not present planned capabilities as working capabilities.
