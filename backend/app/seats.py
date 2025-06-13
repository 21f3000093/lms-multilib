from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models import Seat

router = APIRouter()

@router.get("/seats/view")
def get_seat_map(
    shifts: List[int] = Query(...,alias="shifts[]"), 
    only_empty: bool = False,
    library_id: int = Query(...),
    db: Session = Depends(get_db)
):
    seats = db.query(Seat).filter(Seat.library_id == library_id).all()
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
