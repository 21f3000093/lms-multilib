from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.dependencies import get_db , get_current_admin
from app.models import MonthlyPayment, Student

router = APIRouter()

@router.get("/reminders/pending-fees")
def get_pending_reminders(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    today = date.today()
    upcoming = today + timedelta(days=2)
    current_month = today.strftime("%Y-%m")

    results = []

    payments = db.query(MonthlyPayment).join(Student).filter(
        MonthlyPayment.library_id == admin.library_id,
        MonthlyPayment.month == current_month,
        MonthlyPayment.paid == False,
        Student.status == "active"
    ).all()

    for payment in payments:
        doj = payment.student.date_of_joining
        due_day = doj.day
        try:
            due_date = date(today.year, today.month, due_day)
        except:
            due_date = date(today.year, today.month, 28)

        if due_date <= upcoming:
            results.append({
                "student_name": payment.student.name,
                "student_id": payment.student.id,
                "phone": payment.student.contact,
                "amount": payment.amount,
                "month": payment.month,
                "due_date": due_date.strftime("%d-%m-%Y"),
                "due_date_obj": due_date,  # Add raw date for sorting
            })
            
            
        
    # SORT by due_date_obj (ascending)
    results.sort(key=lambda x: x["due_date_obj"])

    # Optionally, remove 'due_date_obj' before returning to the client:
    for r in results:
        r.pop("due_date_obj", None)
        
    return results
