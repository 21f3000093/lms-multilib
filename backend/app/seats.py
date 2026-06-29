from fastapi import APIRouter, Depends, Query , HTTPException
from sqlalchemy.orm import Session 
from typing import List
from app.dependencies import get_db, require_active_subscription
from app.models import Seat

router = APIRouter()

@router.get("/seats/view")
def get_seat_map(
    shifts: List[int] = Query(...,alias="shifts[]"), 
    only_empty: bool = False,
    library_id: int = Query(...),
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    seats = db.query(Seat).filter(Seat.library_id == admin.library_id).all()
    result = []

    for seat in seats:
        shift_status = []
        skip_seat = False

        for shift in shifts:
            student_id = getattr(seat, f"shift{shift}_student_id")
            is_taken = bool(student_id)

            if only_empty and is_taken:
                skip_seat = True
                break  # Skip this seat if we want only empty but this shift is taken

            shift_status.append(is_taken)

        if not skip_seat:
            result.append({
                "seat_number": seat.seat_number,
                "shifts": shift_status  # True for taken ✅, False for empty ❌
            })


    result.sort(key=lambda s: s["seat_number"])

    return result


@router.get("/seats/{seat_number}/details")
def get_seat_details(
    seat_number: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    from app.models import Student
    
    seat = db.query(Seat).filter(
        Seat.seat_number == seat_number,
        Seat.library_id == admin.library_id
    ).first()
    
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    
    # Get student details for each shift
    shift_details = []
    for shift_num in [1, 2, 3]:
        student_id = getattr(seat, f"shift{shift_num}_student_id")
        student_name = "-"
        photo_url = None
        
        if student_id:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student_name = student.name
                photo_url = student.photo_url
        
        shift_details.append({
            "shift": shift_num,
            "shift_name": ["Morning", "Afternoon", "Evening"][shift_num - 1],
            "student_name": student_name,
            "photo_url": photo_url,
            "is_occupied": bool(student_id)
        })
    
    return {
        "seat_number": seat.seat_number,
        "shifts": shift_details
    }
