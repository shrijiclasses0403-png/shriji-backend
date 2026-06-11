from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str

class SendOTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must be 10 digits")
        return v

class VerifyOTPRequest(BaseModel):
    phone: str
    otp:   str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    name:         str
    student_id:   Optional[str] = None


# ── Student ───────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    id:          str
    name:        str
    class_name:  str
    section:     str = "A"
    phone:       str
    parent_name: str
    dob:         Optional[date] = None
    address:     Optional[str] = None
    fees:        int = 1000
    join_date:   Optional[date] = None
    subjects:    List[str] = []

class StudentUpdate(BaseModel):
    name:        Optional[str] = None
    class_name:  Optional[str] = None
    section:     Optional[str] = None
    phone:       Optional[str] = None
    parent_name: Optional[str] = None
    dob:         Optional[date] = None
    address:     Optional[str] = None
    fees:        Optional[int] = None
    subjects:    Optional[List[str]] = None
    is_active:   Optional[bool] = None

class StudentOut(BaseModel):
    id:          str
    name:        str
    class_name:  str
    section:     str
    phone:       str
    parent_name: str
    dob:         Optional[date]
    address:     Optional[str]
    fees:        int
    join_date:   Optional[date]
    is_active:   bool
    subjects:    List[str] = []

    model_config = {"from_attributes": True}


# ── Fees ──────────────────────────────────────────────────────────────────────

class FeeCreate(BaseModel):
    student_id: str
    month:      str
    amount:     int

class FeeMarkPaid(BaseModel):
    paid_date: date
    method:    str
    notes:     Optional[str] = None

class FeeOut(BaseModel):
    id:         str
    student_id: str
    month:      str
    amount:     int
    paid:       bool
    paid_date:  Optional[date]
    method:     Optional[str]
    notes:      Optional[str]

    model_config = {"from_attributes": True}


# ── Marks ─────────────────────────────────────────────────────────────────────

class MarkCreate(BaseModel):
    student_id: str
    subject:    str
    exam:       str
    max_marks:  int
    marks:      int
    exam_date:  Optional[date] = None

class MarkUpdate(BaseModel):
    subject:   Optional[str] = None
    exam:      Optional[str] = None
    max_marks: Optional[int] = None
    marks:     Optional[int] = None
    exam_date: Optional[date] = None

class MarkOut(BaseModel):
    id:         str
    student_id: str
    subject:    str
    exam:       str
    max_marks:  int
    marks:      int
    exam_date:  Optional[date]

    model_config = {"from_attributes": True}


# ── Attendance ────────────────────────────────────────────────────────────────

class AttendanceUpsert(BaseModel):
    student_id: str
    date:       date
    status:     str                 # present / absent / holiday

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("present", "absent", "holiday"):
            raise ValueError("status must be present, absent, or holiday")
        return v

class AttendanceOut(BaseModel):
    id:         str
    student_id: str
    date:       date
    status:     str

    model_config = {"from_attributes": True}


# ── Notes ─────────────────────────────────────────────────────────────────────

class NoteOut(BaseModel):
    id:          str
    title:       str
    class_name:  str
    subject:     str
    description: Optional[str]
    file_name:   Optional[str]
    file_type:   str
    downloads:   int
    upload_date: Optional[date]

    model_config = {"from_attributes": True}
