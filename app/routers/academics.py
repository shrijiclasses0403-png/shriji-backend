from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.utils.deps import require_admin, require_any
import os, shutil, uuid

# ── Marks ─────────────────────────────────────────────────────────────────────

marks_router = APIRouter(prefix="/marks", tags=["Marks"])


@marks_router.get("/", response_model=List[schemas.MarkOut])
def list_marks(
    student_id: str = None,
    exam: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any),
):
    q = db.query(models.Mark)
    if current_user["role"] == "parent":
        q = q.filter(models.Mark.student_id == current_user.get("student_id"))
    elif student_id:
        q = q.filter(models.Mark.student_id == student_id)
    if exam:
        q = q.filter(models.Mark.exam == exam)
    return q.all()


@marks_router.post("/", response_model=schemas.MarkOut, status_code=201)
def add_mark(
    payload: schemas.MarkCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    mark = models.Mark(**payload.model_dump())
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark


@marks_router.put("/{mark_id}", response_model=schemas.MarkOut)
def update_mark(
    mark_id: str,
    payload: schemas.MarkUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    mark = db.query(models.Mark).filter(models.Mark.id == mark_id).first()
    if not mark:
        raise HTTPException(status_code=404, detail="Mark not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(mark, k, v)
    db.commit()
    db.refresh(mark)
    return mark


@marks_router.delete("/{mark_id}", status_code=204)
def delete_mark(
    mark_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    mark = db.query(models.Mark).filter(models.Mark.id == mark_id).first()
    if not mark:
        raise HTTPException(status_code=404, detail="Mark not found")
    db.delete(mark)
    db.commit()


# ── Attendance ─────────────────────────────────────────────────────────────────

attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])


@attendance_router.get("/", response_model=List[schemas.AttendanceOut])
def list_attendance(
    student_id: str = None,
    month: str = None,            # YYYY-MM
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any),
):
    from sqlalchemy import cast, String
    q = db.query(models.Attendance)
    if current_user["role"] == "parent":
        q = q.filter(models.Attendance.student_id == current_user.get("student_id"))
    elif student_id:
        q = q.filter(models.Attendance.student_id == student_id)
    if month:
        q = q.filter(cast(models.Attendance.date, String).like(f"{month}%"))
    return q.order_by(models.Attendance.date.desc()).all()


@attendance_router.post("/upsert", response_model=schemas.AttendanceOut)
def upsert_attendance(
    payload: schemas.AttendanceUpsert,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == payload.student_id,
        models.Attendance.date == payload.date,
    ).first()

    if existing:
        existing.status = payload.status
        db.commit()
        db.refresh(existing)
        return existing

    record = models.Attendance(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── Notes ──────────────────────────────────────────────────────────────────────

notes_router = APIRouter(prefix="/notes", tags=["Notes"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@notes_router.get("/", response_model=List[schemas.NoteOut])
def list_notes(
    class_name: str = None,
    subject: str = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_any),
):
    q = db.query(models.Note)
    if class_name:
        q = q.filter(models.Note.class_name == class_name)
    if subject:
        q = q.filter(models.Note.subject == subject)
    return q.order_by(models.Note.created_at.desc()).all()


@notes_router.post("/", response_model=schemas.NoteOut, status_code=201)
async def upload_note(
    title:       str = Form(...),
    class_name:  str = Form(...),
    subject:     str = Form(...),
    description: str = Form(None),
    file:        UploadFile = File(...),
    db:          Session = Depends(get_db),
    _:           dict = Depends(require_admin),
):
    # Save file to uploads/
    ext       = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path  = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    note = models.Note(
        title       = title,
        class_name  = class_name,
        subject     = subject,
        description = description,
        file_name   = file.filename,
        file_path   = file_path,
        file_type   = ext.lstrip(".") or "pdf",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@notes_router.get("/{note_id}/download")
def download_note(
    note_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_any),
):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note or not note.file_path or not os.path.exists(note.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    note.downloads += 1
    db.commit()

    return FileResponse(
        path        = note.file_path,
        filename    = note.file_name,
        media_type  = "application/octet-stream",
    )


@notes_router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Delete file from disk
    if note.file_path and os.path.exists(note.file_path):
        os.remove(note.file_path)

    db.delete(note)
    db.commit()
