"""Helpers for building installment schedules for salary advances."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange

CENT = Decimal("0.01")


def money(v: Decimal) -> Decimal:
    return v.quantize(CENT, rounding=ROUND_HALF_UP)


def build_installment_schedule(
    total_amount: Decimal,
    installment_count: int,
    first_payroll_month: date,
) -> list[dict]:
    if installment_count < 1 or installment_count > 36:
        raise ValueError("عدد الأقساط يجب أن يكون بين 1 و 36.")
    if total_amount <= 0:
        raise ValueError("مبلغ السلفة يجب أن يكون موجبًا.")

    base = money(total_amount / Decimal(installment_count))
    schedule = []
    remaining = total_amount
    year, month = first_payroll_month.year, first_payroll_month.month

    for i in range(1, installment_count + 1):
        if i == installment_count:
            amount = money(remaining)
        else:
            amount = base
            remaining -= amount
        schedule.append({
            "installment_number": i,
            "amount": amount,
            "payroll_month": date(year, month, 1),
            "status": "scheduled",
        })
        # next month
        month += 1
        if month > 12:
            month = 1
            year += 1
    return schedule
