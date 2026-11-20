"""Safe local command agent for the HR assistant — Version 2.

The language model may propose an action, but it never gets direct database access.
Only the fixed allowlist of business operations can mutate data, and every operation
goes through the confirmation gateway (prepare → show old/new → explicit confirm → execute).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.ai_assistant import ask_local_model_json, local_model_status
from app.db import SessionLocal
from app.employee_codes import allocate_employee_code
from app.models import (
    AdvanceRequest, AttendanceDailyRecord, AttendanceMonth, Department, Branch,
    Employee, EmployeeChange, EmployeeServicePeriod, LeaveRecord, LeaveType,
    PayrollRun, StaffAction, AuditLog,
)

ALLOWED_ACTIONS = {
    "create_employee", "edit_employee", "transfer_employee", "archive_employee", "rehire_employee",
    "create_leave", "confirm_leave", "cancel_leave", "adjust_leave_balance",
    "create_advance", "approve_advance", "reject_advance", "mark_advance_paid",
    "create_staff_action", "approve_staff_action", "cancel_staff_action",
    "approve_attendance_day", "approve_attendance_month",
    "approve_payroll_run", "close_payroll_run", "reopen_payroll_run",
}


def _context() -> dict[str, Any]:
    with SessionLocal() as db:
        employees = db.scalars(select(Employee).limit(200)).all()
        departments = db.scalars(select(Department)).all()
        leave_types = db.scalars(select(LeaveType)).all()
        advances = db.scalars(select(AdvanceRequest).order_by(AdvanceRequest.id.desc()).limit(50)).all()
        staff_actions = db.scalars(select(StaffAction).order_by(StaffAction.id.desc()).limit(50)).all()
        attendance_months = db.scalars(select(AttendanceMonth).order_by(AttendanceMonth.id.desc()).limit(12)).all()
        payroll_runs = db.scalars(select(PayrollRun).order_by(PayrollRun.id.desc()).limit(12)).all()
        return {
            "employees": [
                {
                    "id": e.id, "code": e.employee_code, "name": e.full_name,
                    "status": e.status, "department_id": e.department_id,
                    "basic_salary": str(e.basic_salary), "hire_date": e.hire_date.isoformat(),
                }
                for e in employees
            ],
            "departments": [{"id": d.id, "name": d.name, "name_ar": d.name_ar} for d in departments],
            "leave_types": [{"id": t.id, "code": t.code, "name_ar": t.name_ar} for t in leave_types],
            "advances": [
                {"id": a.id, "employee_id": a.employee_id, "amount": str(a.amount),
                 "status": a.status, "advance_type": a.advance_type}
                for a in advances
            ],
            "staff_actions": [
                {"id": s.id, "employee_id": s.employee_id, "kind": s.kind, "status": s.status}
                for s in staff_actions
            ],
            "attendance_months": [
                {"id": m.id, "period_start": m.period_start.isoformat(), "status": m.status}
                for m in attendance_months
            ],
            "payroll_runs": [
                {"id": r.id, "period_start": r.period_start.isoformat(), "status": r.status}
                for r in payroll_runs
            ],
        }


def build_plan(question: str) -> dict[str, Any]:
    """Turn a natural language command into a structured plan (no side effects)."""
    status = local_model_status()
    if not status["available"]:
        return _fallback_plan(question)

    context = _context()
    system = (
        "أنت مساعد موارد بشرية لنظام فندق M.Y. Business Hotel. "
        "حوّل أمر المسؤول إلى JSON فقط بدون Markdown. "
        "action يجب أن يكون واحدًا من: " + ", ".join(sorted(ALLOWED_ACTIONS)) + ". "
        "أضف دائمًا: summary (عربي)، old_values (قاموس)، new_values (قاموس)، risks (قائمة). "
        "لا تخترع IDs؛ استخدم فقط الموجود في البيانات. "
        "إذا كان الأمر استعلامًا فقط وليس تنفيذًا، اجعل action = null واملأ summary بالرد."
    )
    prompt = f"الأمر: {question}\n\nالبيانات المتاحة:\n{json.dumps(context, ensure_ascii=False)}"
    try:
        plan = ask_local_model_json(prompt, system=system)
        if not isinstance(plan, dict):
            raise ValueError("Invalid plan shape")
        plan.setdefault("summary", "خطة جاهزة للمراجعة")
        plan.setdefault("old_values", {})
        plan.setdefault("new_values", {})
        plan.setdefault("risks", [])
        return plan
    except Exception as exc:
        return {
            "action": None,
            "summary": f"تعذر بناء خطة تلقائية: {exc}. يمكنك إعادة صياغة الأمر أو تنفيذ العملية من الواجهة العادية.",
            "old_values": {},
            "new_values": {},
            "risks": ["النموذج المحلي غير متاح أو أعاد استجابة غير صالحة"],
        }


def _fallback_plan(question: str) -> dict[str, Any]:
    return {
        "action": None,
        "summary": (
            "المساعد المحلي غير متاح حاليًا. يمكنك استخدام الواجهة العادية لتنفيذ العمليات، "
            "أو تشغيل نموذج Ollama محليًا ثم إعادة المحاولة."
        ),
        "old_values": {},
        "new_values": {},
        "risks": ["المساعد الذكي غير متصل"],
        "raw_question": question,
    }


def execute_plan(plan: dict[str, Any], actor: str) -> str:
    """Execute a previously confirmed plan. Called only from the approval gateway."""
    action = plan.get("action")
    if not action or action not in ALLOWED_ACTIONS:
        raise ValueError("لا توجد عملية قابلة للتنفيذ في هذه الخطة.")

    with SessionLocal.begin() as db:
        if action == "create_employee":
            code = allocate_employee_code(db)
            emp = Employee(
                employee_code=code,
                full_name=str(plan.get("full_name") or "").strip(),
                national_id=plan.get("national_id"),
                phone=plan.get("phone"),
                address=plan.get("address"),
                position=plan.get("position"),
                department_id=int(plan["department_id"]),
                branch_id=int(plan["branch_id"]) if plan.get("branch_id") else None,
                hire_date=date.fromisoformat(plan["hire_date"]) if plan.get("hire_date") else date.today(),
                basic_salary=Decimal(str(plan.get("basic_salary") or "0")),
                daily_hours=Decimal(str(plan.get("daily_hours") or "8")),
                fingerprint_id=plan.get("fingerprint_id"),
                status="active",
            )
            if not emp.full_name:
                raise ValueError("اسم الموظف مطلوب.")
            db.add(emp)
            db.flush()
            db.add(EmployeeServicePeriod(employee_id=emp.id, start_date=emp.hire_date))
            db.add(AuditLog(
                actor=actor, action="employee_created", entity_type="employee",
                entity_id=str(emp.id), new_value=f"{code} | {emp.full_name}",
                reason=plan.get("reason") or "إنشاء عبر المساعد",
            ))
            return f"تم إنشاء الموظف {emp.full_name} بالكود {code}."

        if action == "archive_employee":
            emp = db.get(Employee, int(plan["employee_id"]))
            if emp is None:
                raise ValueError("الموظف غير موجود.")
            old = emp.status
            emp.status = "archived"
            db.add(EmployeeChange(
                employee_id=emp.id, field_name="status",
                old_value=old, new_value="archived",
                effective_date=date.today(), reason=plan.get("reason") or "أرشفة",
                actor=actor,
            ))
            db.add(AuditLog(
                actor=actor, action="employee_archived", entity_type="employee",
                entity_id=str(emp.id), previous_value=old, new_value="archived",
                reason=plan.get("reason") or "",
            ))
            return f"تم أرشفة الموظف {emp.full_name} ({emp.employee_code})."

        if action == "create_leave":
            from app.leave_workflow import create_leave
            record = create_leave(
                db,
                employee_id=int(plan["employee_id"]),
                leave_type_id=int(plan["leave_type_id"]),
                start_date=date.fromisoformat(plan["start_date"]),
                end_date=date.fromisoformat(plan["end_date"]),
                charged_days=Decimal(str(plan.get("charged_days") or "1")),
                reason=plan.get("reason"),
                actor=actor,
            )
            return f"تم تسجيل إجازة رقم {record.id} بحالة pending."

        if action == "confirm_leave":
            from app.leave_workflow import confirm_leave
            record = db.get(LeaveRecord, int(plan["record_id"]))
            if record is None:
                raise ValueError("سجل الإجازة غير موجود.")
            confirm_leave(db, record, actor)
            return f"تم تأكيد الإجازة رقم {record.id}."

        if action == "cancel_leave":
            from app.leave_workflow import cancel_leave
            record = db.get(LeaveRecord, int(plan["record_id"]))
            if record is None:
                raise ValueError("سجل الإجازة غير موجود.")
            cancel_leave(db, record, actor, plan.get("reason"))
            return f"تم إلغاء الإجازة رقم {record.id}."

        if action == "approve_payroll_run":
            run = db.get(PayrollRun, int(plan["payroll_run_id"]))
            if run is None:
                raise ValueError("مسير الرواتب غير موجود.")
            if run.status != "draft":
                raise ValueError("لا يمكن اعتماد مسير ليس في حالة draft.")
            run.status = "approved"
            run.approved_at = datetime.utcnow()
            db.add(AuditLog(
                actor=actor, action="payroll_approved", entity_type="payroll_run",
                entity_id=str(run.id), previous_value="draft", new_value="approved",
            ))
            return f"تم اعتماد مسير الرواتب رقم {run.id}."

        if action == "close_payroll_run":
            run = db.get(PayrollRun, int(plan["payroll_run_id"]))
            if run is None:
                raise ValueError("مسير الرواتب غير موجود.")
            if run.status != "approved":
                raise ValueError("يجب اعتماد المسير قبل إغلاقه.")
            run.status = "closed"
            run.closed_at = datetime.utcnow()
            db.add(AuditLog(
                actor=actor, action="payroll_closed", entity_type="payroll_run",
                entity_id=str(run.id), previous_value="approved", new_value="closed",
            ))
            return f"تم إغلاق مسير الرواتب رقم {run.id}."

        raise ValueError(f"العملية '{action}' مسجلة في القائمة لكنها لم تُنفَّذ بعد في هذا الإصدار. سيتم استكمالها.")
