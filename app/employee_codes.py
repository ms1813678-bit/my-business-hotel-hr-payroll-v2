from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import Employee


def allocate_employee_code(db: Session) -> str:
    """Allocate the next non-reusable MY-XXXX code."""
    result = db.execute(
        text("SELECT nextval('employee_code_seq')")
    ).scalar()
    code = f"MY-{int(result):04d}"
    existing = db.scalar(select(Employee).where(Employee.employee_code == code))
    if existing is not None:
        raise RuntimeError(f"Employee code collision for {code}")
    return code
