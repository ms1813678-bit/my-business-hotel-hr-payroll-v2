"""Approval gateway for the local HR AI command agent (Version 2.1).

The model may prepare a plan, but every state-changing command must pass through
this gateway. Approval tokens are single-use, hashed at rest, time-limited, and
bound to the administrator who requested the plan and to the exact plan hash.

Version 2.1 confirmation contract:
1. prepare_command builds a plan and returns a structured payload for the UI
2. UI must display summary + old_values + new_values + risks
3. Admin must explicitly confirm (token is bound to the plan)
4. approve_command executes only if the plan hash still matches
5. Every step is audited
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select

from app.ai_agent import build_plan, execute_plan
from app.db import SessionLocal
from app.models import AICommandApproval, AIConversationMessage, AuditLog

APPROVAL_TTL_MINUTES = 10


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def plan_hash(plan: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(plan).encode("utf-8")).hexdigest()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _memory(actor: str, role: str, content: str) -> None:
    with SessionLocal.begin() as db:
        db.add(AIConversationMessage(actor=actor, role=role, content=content[:10000]))


def recent_memory(actor: str, limit: int = 12) -> list[dict[str, str]]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(AIConversationMessage)
            .where(AIConversationMessage.actor == actor)
            .order_by(AIConversationMessage.id.desc())
            .limit(limit)
        ).all()
    rows.reverse()
    return [{"role": row.role, "content": row.content} for row in rows]


def enrich_plan_for_display(plan: dict[str, Any]) -> dict[str, Any]:
    """Ensure old_values / new_values / risks exist for confirmation UI."""
    action = str(plan.get("action") or "")
    old_values = dict(plan.get("old_values") or {})
    new_values = dict(plan.get("new_values") or {})
    risks = list(plan.get("risks") or [])

    for key in (
        "full_name", "basic_salary", "position", "phone", "department_id", "branch_id",
        "amount", "installment_count", "charged_days", "start_date", "end_date",
        "clock_in", "clock_out", "kind", "category", "title", "employee_id",
        "leave_type_id", "payroll_run_id", "advance_id",
    ):
        if key in plan and plan[key] is not None and key not in new_values:
            new_values[key] = plan[key]

    if action in {"archive_employee", "rehire_employee"}:
        risks.append("يؤثر على الحالة الوظيفية للموظف وسجل الخدمة.")
    if action in {"approve_payroll_run", "close_payroll_run"}:
        risks.append("عملية مالية نهائية أو قريبة من النهائية — راجع المسير جيدًا قبل التأكيد.")
    if action == "reopen_payroll_run":
        risks.append("إعادة فتح مسير رواتب مغلق قد تؤثر على الأقساط والخصومات المطبقة.")
    if action.startswith("approve_") or action.startswith("close_"):
        risks.append("لا يمكن التراجع بسهولة بعد الاعتماد في بعض الحالات.")
    if action in {"create_advance", "approve_advance"}:
        risks.append("سلفة تؤثر على صافي الراتب والأقساط المستقبلية.")
    if not risks:
        risks.append("تأكد من صحة البيانات قبل التأكيد.")

    plan = dict(plan)
    plan["old_values"] = old_values
    plan["new_values"] = new_values
    plan["risks"] = risks
    return plan


def prepare_command(question: str, actor: str) -> dict[str, Any]:
    """Build a plan without mutating data. Returns confirmation payload for the UI."""
    history = recent_memory(actor, limit=8)
    history_text = "\\n".join(f"{item['role']}: {item['content']}" for item in history)
    planning_question = question
    if history_text:
        planning_question = (
            f"السياق السابق للمحادثة (للفهم فقط):\\n{history_text}\\n\\nالأمر الحالي: {question}"
        )
    plan = enrich_plan_for_display(build_plan(planning_question))
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=APPROVAL_TTL_MINUTES)
    summary = str(plan.get("summary") or "تم إعداد خطة للتنفيذ بعد الموافقة.")
    old_values = plan.get("old_values") or {}
    new_values = plan.get("new_values") or {}
    risks = plan.get("risks") or []

    with SessionLocal.begin() as db:
        db.add(AICommandApproval(
            token_hash=_token_hash(token),
            actor=actor,
            question=question,
            plan_json=_canonical_json(plan),
            plan_hash=plan_hash(plan),
            status="pending",
            created_at=now,
            expires_at=expires,
        ))
        db.add(AuditLog(
            actor=actor,
            action="ai_command_proposed",
            entity_type="ai_command",
            entity_id=_token_hash(token)[:16],
            new_value=f"action={plan.get('action')}; plan_hash={plan_hash(plan)[:12]}",
            reason=summary[:500],
        ))
    _memory(actor, "user", question)
    _memory(actor, "assistant", f"خطة معدة: {summary}")

    return {
        "status": "awaiting_confirmation",
        "confirmation_token": token,
        "token": token,
        "expires_at": expires.isoformat(),
        "summary": summary,
        "action": plan.get("action"),
        "old_values": old_values,
        "new_values": new_values,
        "risks": risks,
        "plan": plan,
        "plan_preview": {k: v for k, v in plan.items() if k not in {"old_values", "new_values", "risks"}},
        "message": (
            "تم تجهيز العملية. راجع الملخص والبيانات القديمة والجديدة ثم اضغط "
            "«تأكيد التنفيذ» فقط إذا كنت موافقًا. أي تعديل على الأمر يتطلب تجهيزًا جديدًا."
        ),
    }


def reject_command(token: str, actor: str, reason: str = "رفض من المسؤول") -> str:
    now = datetime.now(timezone.utc)
    with SessionLocal.begin() as db:
        approval = db.scalar(
            select(AICommandApproval)
            .where(AICommandApproval.token_hash == _token_hash(token))
            .with_for_update()
        )
        if approval is None or approval.actor != actor:
            raise ValueError("طلب الموافقة غير موجود.")
        if approval.status != "pending":
            raise ValueError("هذا الطلب لم يعد قابلًا للرفض.")
        if approval.expires_at <= now:
            approval.status = "expired"
            raise ValueError("انتهت صلاحية طلب الموافقة.")
        approval.status = "rejected"
        approval.rejected_at = now
        db.add(AuditLog(
            actor=actor,
            action="ai_command_rejected",
            entity_type="ai_command",
            entity_id=str(approval.id),
            reason=reason,
        ))
    _memory(actor, "assistant", "تم رفض العملية ولم يتم تغيير بيانات النظام.")
    return "تم رفض العملية. لم يتم تغيير أي بيانات."


def approve_command(token: str, actor: str) -> str:
    """Execute only after explicit confirmation. Bound to the exact plan hash."""
    now = datetime.now(timezone.utc)
    with SessionLocal.begin() as db:
        approval = db.scalar(
            select(AICommandApproval)
            .where(AICommandApproval.token_hash == _token_hash(token))
            .with_for_update()
        )
        if approval is None or approval.actor != actor:
            raise ValueError("طلب الموافقة غير موجود.")
        if approval.status != "pending":
            raise ValueError("هذا الطلب سبق التعامل معه ولا يمكن تنفيذه مرة أخرى.")
        if approval.expires_at <= now:
            approval.status = "expired"
            db.add(AuditLog(
                actor=actor,
                action="ai_command_expired",
                entity_type="ai_command",
                entity_id=str(approval.id),
                reason="انتهت صلاحية طلب الموافقة.",
            ))
            raise ValueError("انتهت صلاحية طلب الموافقة.")
        plan = json.loads(approval.plan_json)
        if plan_hash(plan) != approval.plan_hash:
            approval.status = "invalidated"
            raise ValueError("خطة التنفيذ لم تعد مطابقة للخطة التي تم عرضها.")
        approval.status = "executing"
        approval.approved_at = now
        db.add(AuditLog(
            actor=actor,
            action="ai_command_approved",
            entity_type="ai_command",
            entity_id=str(approval.id),
            new_value=f"plan_hash={approval.plan_hash}",
            reason="موافقة صريحة من مسؤول الموارد البشرية.",
        ))

    try:
        message = execute_plan(plan, actor)
    except Exception as exc:
        with SessionLocal.begin() as db:
            approval = db.scalar(
                select(AICommandApproval).where(AICommandApproval.token_hash == _token_hash(token))
            )
            if approval is not None:
                approval.status = "failed"
                approval.failure_reason = str(exc)[:2000]
                db.add(AuditLog(
                    actor=actor,
                    action="ai_command_failed",
                    entity_type="ai_command",
                    entity_id=str(approval.id),
                    reason=str(exc)[:2000],
                ))
        raise

    with SessionLocal.begin() as db:
        approval = db.scalar(
            select(AICommandApproval).where(AICommandApproval.token_hash == _token_hash(token))
        )
        if approval is None or approval.status != "executing":
            raise RuntimeError("حالة الموافقة غير صالحة بعد التنفيذ.")
        approval.status = "consumed"
        approval.consumed_at = datetime.now(timezone.utc)
        db.add(AuditLog(
            actor=actor,
            action="ai_command_executed",
            entity_type="ai_command",
            entity_id=str(approval.id),
            new_value=f"plan_hash={approval.plan_hash}",
            reason=message,
        ))
    _memory(actor, "assistant", message)
    return message
