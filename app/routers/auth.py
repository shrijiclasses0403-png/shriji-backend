from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.security import verify_password, create_access_token
from app.services.otp_service import generate_otp, send_otp_fast2sms, save_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/admin/login", response_model=schemas.TokenResponse)
def admin_login(payload: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_access_token({"sub": admin.id, "role": "admin", "name": admin.name})
    return {"access_token": token, "token_type": "bearer", "role": "admin", "name": admin.name}


@router.post("/parent/send-otp")
async def send_otp(payload: schemas.SendOTPRequest, db: Session = Depends(get_db)):
    # Check if phone is registered
    student = db.query(models.Student).filter(
        models.Student.phone == payload.phone,
        models.Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered. Please contact admin."
        )

    otp = generate_otp(6)
    save_otp(db, payload.phone, otp)

    try:
        await send_otp_fast2sms(payload.phone, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    return {"message": "OTP sent successfully", "phone": payload.phone}


@router.post("/parent/verify-otp", response_model=schemas.TokenResponse)
def verify_otp_route(payload: schemas.VerifyOTPRequest, db: Session = Depends(get_db)):
    is_valid = verify_otp(db, payload.phone, payload.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    student = db.query(models.Student).filter(models.Student.phone == payload.phone).first()
    token = create_access_token({
        "sub":        payload.phone,
        "role":       "parent",
        "name":       student.parent_name,
        "student_id": student.id,
    })
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         "parent",
        "name":         student.parent_name,
        "student_id":   student.id,
    }
