from decimal import Decimal, ROUND_HALF_UP
from datetime import date


def hourly_rate(basic_salary: Decimal, daily_hours: Decimal) -> Decimal:
    if daily_hours <= 0:
        raise ValueError("daily_hours must be positive")
    return (basic_salary / (daily_hours * 30)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def prorate_new_hire(basic_salary: Decimal, hire_date: date, period_start: date, period_end: date) -> Decimal:
    if hire_date > period_end:
        return Decimal("0.00")
    effective_start = max(hire_date, period_start)
    days_in_period = (period_end - period_start).days + 1
    worked_days = (period_end - effective_start).days + 1
    if worked_days <= 0:
        return Decimal("0.00")
    return (basic_salary * Decimal(worked_days) / Decimal(days_in_period)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
