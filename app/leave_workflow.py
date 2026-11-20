"""Business rules for administrator-managed leave records and balance history."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AuditLog,
    LeaveBalanceTransaction,
    LeaveRecord,
    LeaveType,
    Employee,
)


def create_leave(
    db: Session,
    *,
    employee_id: int,
    leave_type_id: int,
    start_date,
    end_date,
    charged_days: Decimal,
    reason: str | None,
    actor: str,
) -> LeaveRecord:
    emp = db.get(Employee, employee_id)
    if emp is None:
        raise ValueError("الموظف غير موجود.")
    lt = db.get(LeaveType, leave_type_id)
    if lt is None:
        raise ValueError("نوع الإجازة غير موجود.")
    if end_date < start_date:
        raise ValueError("تاريخ النهاية قبل البداية.")
    if charged_days < 0:
        raise ValueError("عدد الأيام لا يمكن أن يكون سالبًا.")

    record = LeaveRecord(
        employee_id=employee_id,
        leave_type_id=leave_type_id,
        start_date=start_date,
        end_date=end_date,
        charged_days=charged_days,
        reason=reason,
        status="pending",
        created_by=actor,
    )
    db.add(record)
    db.flush()
    db.add(AuditLog(
        actor=actor,
        action="leave_created",
        entity_type="leave_record",
        entity_id=str(record.id),
        new_value=f"employee={employee_id}; type={leave_type_id}; days={charged_days}",
        reason=reason or "",
    ))
    return record


def confirm_leave(db: Session, record: LeaveRecord, actor: str) -> None:
    if record.status != "pending":
        raise ValueError("لا يمكن تأكيد إجازة ليست في حالة pending.")
    record.status = "confirmed"
    record.confirmed_at = datetime.utcnow()
    record.confirmed_by = actor
    # Deduct balance
    db.add(LeaveBalanceTransaction(
        employee_id=record.employee_id,
        leave_type_id=record.leave_type_id,
        transaction_type="deduction",
        days=-record.charged_days,
        related_leave_id=record.id,
        reason=f"تأكيد إجازة #{record.id}",
        created_by=actor,
    ))
    db.add(AuditLog(
        actor=actor,
        action="leave_confirmed",
        entity_type="leave_record",
        entity_id=str(record.id),
        reason="تأكيد الإجازة وخصم الرصيد",
    ))


def cancel_leave(db: Session, record: LeaveRecord, actor: str, reason: str | None = None) -> None:
    if record.status == "cancelled":
        raise ValueError("الإجازة ملغاة مسبقًا.")
    previous = record.status
    record.status = "cancelled"
    record.cancelled_at = datetime.utcnow()
    record.cancelled_by = actor
    if previous == "confirmed":
        # Restore balance
        db.add(LeaveBalanceTransaction(
            employee_id=record.employee_id,
            leave_type_id=record.leave_type_id,
            transaction_type="restoration",
            days=record.charged_days,
            related_leave_id=record.id,
            reason=f"إلغاء إجازة #{record.id}",
            created_by=actor,
        ))
    db.add(AuditLog(
        actor=actor,
        action="leave_cancelled",
        entity_type="leave_record",
        entity_id=str(record.id),
        previous_value=previous,
        new_value="cancelled",
        reason=reason or "",
    ))


def add_balance_entry(
    db: Session,
    *,
    employee_id: int,
    leave_type_id: int,
    days: Decimal,
    transaction_type: str,
    reason: str,
    actor: str,
) -> LeaveBalanceTransaction:
    if transaction_type not in {"opening", "adjustment", "restoration", "deduction"}:
        raise ValueError("نوع حركة الرصيد غير مدعوم.")
    entry = LeaveBalanceTransaction(
        employee_id=employee_id,
        leave_type_id=leave_type_id,
        transaction_type=transaction_type,
        days=days,
        reason=reason,
        created_by=actor,
    )
    db.add(entry)
    db.flush()
    db.add(AuditLog(
        actor=actor,
        action="leave_balance_adjusted",
        entity_type="leave_balance",
        entity_id=str(entry.id),
        new_value=f"days={days}; type={transaction_type}",
        reason=reason,
    ))
    return entry
