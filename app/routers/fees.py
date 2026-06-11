from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.utils.deps import require_admin, require_any

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("/", response_model=List[schemas.FeeOut])
def list_fees(
    student_id: str = None,
    month: str = None,
    paid: bool = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any),
):
    q = db.query(models.FeeRecord)

    # Parent can only see their child's fees
    if current_user["role"] == "parent":
        q = q.filter(models.FeeRecord.student_id == current_user.get("student_id"))
    elif student_id:
        q = q.filter(models.FeeRecord.student_id == student_id)

    if month:
        q = q.filter(models.FeeRecord.month == month)
    if paid is not None:
        q = q.filter(models.FeeRecord.paid == paid)

    return q.all()


@router.post("/", response_model=schemas.FeeOut, status_code=201)
def create_fee_record(
    payload: schemas.FeeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    # Avoid duplicate for same student+month
    existing = db.query(models.FeeRecord).filter(
        models.FeeRecord.student_id == payload.student_id,
        models.FeeRecord.month == payload.month,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Fee record already exists for this month")

    record = models.FeeRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{fee_id}/mark-paid", response_model=schemas.FeeOut)
def mark_fee_paid(
    fee_id: str,
    payload: schemas.FeeMarkPaid,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    record = db.query(models.FeeRecord).filter(models.FeeRecord.id == fee_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Fee record not found")

    record.paid      = True
    record.paid_date = payload.paid_date
    record.method    = payload.method
    record.notes     = payload.notes
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{fee_id}", status_code=204)
def delete_fee(
    fee_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    record = db.query(models.FeeRecord).filter(models.FeeRecord.id == fee_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Fee record not found")
    db.delete(record)
    db.commit()
