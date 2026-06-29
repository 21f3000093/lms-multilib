import time
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db, require_active_subscription
from app.services.storage import (
    StorageConfigurationError,
    delete_student_photo,
    get_student_photo_key,
    upload_student_photo,
)


router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _detect_image_type(file_bytes: bytes) -> str | None:
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(file_bytes) >= 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return "webp"
    return None


def _validate_student_photo(upload_file: UploadFile, file_bytes: bytes) -> None:
    extension = Path(upload_file.filename or "").suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are allowed")

    content_type = (upload_file.content_type or "").lower()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller")

    detected_type = _detect_image_type(file_bytes)
    if detected_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")


def _get_student_or_404(db: Session, student_id: int, library_id: int):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id, models.Student.library_id == library_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/student-photo")
async def upload_photo(
    student_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_active_subscription),
):
    _get_student_or_404(db, student_id, admin.library_id)

    file_bytes = await file.read()
    _validate_student_photo(file, file_bytes)

    timestamp = int(time.time() * 1000)
    object_key = f"students/{admin.library_id}/{student_id}_{timestamp}.webp"

    try:
        photo_url = upload_student_photo(
            file_bytes,
            object_key,
            content_type=(file.content_type or "image/webp"),
        )
    except StorageConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except RuntimeError:
        raise HTTPException(status_code=502, detail="Photo upload failed")

    return {"photo_url": photo_url}


@router.delete("/student-photo")
def delete_photo(
    photo_url: str = Body(..., embed=True),
    admin=Depends(require_active_subscription),
):
    try:
        object_key = get_student_photo_key(photo_url)
    except StorageConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    if not object_key or not object_key.startswith(f"students/{admin.library_id}/"):
        raise HTTPException(status_code=400, detail="Invalid student photo URL")

    try:
        deleted = delete_student_photo(photo_url)
    except StorageConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except RuntimeError:
        raise HTTPException(status_code=502, detail="Photo delete failed")

    return {"deleted": deleted}
