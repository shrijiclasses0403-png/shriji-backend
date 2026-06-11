from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.utils.deps import require_admin, require_any

router = APIRouter(prefix="/students", tags=["Students"])


def _build_student_out(s: models.Student) -> schemas.StudentOut:
    return schemas.StudentOut(
        id          = s.id,
        name        = s.name,
        class_name  = s.class_name,
        section     = s.section,
        phone       = s.phone,
        parent_name = s.parent_name,
        dob         = s.dob,
        address     = s.address,
        fees        = s.fees,
        join_date   = s.join_date,
        is_active   = s.is_active,
        subjects    = [sub.subject for sub in s.subjects],
    )


@router.get("/", response_model=List[schemas.StudentOut])
def list_students(
    class_name: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = db.query(models.Student).filter(models.Student.is_active == True)
    if class_name:
        q = q.filter(models.Student.class_name == class_name)
    if search:
        q = q.filter(
            models.Student.name.ilike(f"%{search}%") |
            models.Student.id.ilike(f"%{search}%") |
            models.Student.parent_name.ilike(f"%{search}%")
        )
    return [_build_student_out(s) for s in q.all()]


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any),
):
    # Parent can only view their own child
    if current_user["role"] == "parent" and current_user.get("student_id") != student_id:
        raise HTTPException(status_code=403, detail="Access denied")

    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return _build_student_out(s)


@router.post("/", response_model=schemas.StudentOut, status_code=201)
def create_student(
    payload: schemas.StudentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    if db.query(models.Student).filter(models.Student.id == payload.id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")
    if db.query(models.Student).filter(models.Student.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    student = models.Student(
        id          = payload.id,
        name        = payload.name,
        class_name  = payload.class_name,
        section     = payload.section,
        phone       = payload.phone,
        parent_name = payload.parent_name,
        dob         = payload.dob,
        address     = payload.address,
        fees        = payload.fees,
        join_date   = payload.join_date,
    )
    db.add(student)
    db.flush()

    for sub in payload.subjects:
        db.add(models.StudentSubject(student_id=student.id, subject=sub))

    db.commit()
    db.refresh(student)
    return _build_student_out(student)


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: str,
    payload: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = payload.model_dump(exclude_unset=True)
    subjects = update_data.pop("subjects", None)

    for key, val in update_data.items():
        setattr(student, key, val)

    if subjects is not None:
        db.query(models.StudentSubject).filter(models.StudentSubject.student_id == student_id).delete()
        for sub in subjects:
            db.add(models.StudentSubject(student_id=student_id, subject=sub))

    db.commit()
    db.refresh(student)
    return _build_student_out(student)


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Soft delete
    student.is_active = False
    db.commit()
