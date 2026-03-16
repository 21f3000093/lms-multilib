from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.dependencies import get_db, require_active_subscription
from app.models import MonthlyPayment, Student
import calendar

router = APIRouter()

@router.get("/reminders/pending-fees/{month}")
def get_pending_reminders(
    month: str,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    """
    Get pending fee reminders for a specific month
    month format: YYYY-MM (e.g., "2025-08")
    """
    # Parse the month parameter
    try:
        year, month_num = map(int, month.split('-'))
    except Exception:
        # Fallback to current month if invalid format
        today = date.today()
        year, month_num = today.year, today.month
        month = f"{year:04d}-{month_num:02d}"

    results = []

    # Get all unpaid payments for the selected month
    payments = db.query(MonthlyPayment).join(Student).filter(
        MonthlyPayment.library_id == admin.library_id,
        MonthlyPayment.month == month,
        MonthlyPayment.paid == False,
        Student.status == "active"
    ).all()

    for payment in payments:
        doj = payment.student.date_of_joining
        if doj:
            due_day = doj.day
            try:
                due_date = date(year, month_num, due_day)
            except ValueError:
                # Handle invalid dates (e.g., Feb 30)
                last_day = calendar.monthrange(year, month_num)[1]
                due_date = date(year, month_num, min(due_day, last_day))
        else:
            # If no joining date, set due date to 1st of month
            due_date = date(year, month_num, 1)
            
        if due_date < date.today()+timedelta(days=2):
            # Payment is overdue            
            results.append({
                "student_name": payment.student.name,
                "student_id": payment.student.id,
                "phone": payment.student.contact,
                "amount": payment.amount,
                "month": payment.month,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "due_date_sort": due_date,  # For sorting
            })

    # Sort by due date
    results.sort(key=lambda x: x["due_date_sort"])
    
    # Remove sort key before returning
    for r in results:
        r.pop("due_date_sort", None)
        
    return results

# Keep the old endpoint for backward compatibility (optional)
@router.get("/reminders/pending-fees")
def get_current_month_reminders(
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    """
    Get pending reminders for current month (backward compatibility)
    """
    current_month = date.today().strftime("%Y-%m")
    return get_pending_reminders(current_month, db, admin)
