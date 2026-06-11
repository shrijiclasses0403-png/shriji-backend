from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


def gen_uuid():
    return str(uuid.uuid4())


class Admin(Base):
    __tablename__ = "admins"

    id         = Column(String, primary_key=True, default=gen_uuid)
    username   = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name       = Column(String, nullable=False, default="Admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Student(Base):
    __tablename__ = "students"

    id          = Column(String, primary_key=True)          # SJC001
    name        = Column(String, nullable=False)
    class_name  = Column(String, nullable=False)            # '10th'
    section     = Column(String, default="A")
    phone       = Column(String, unique=True, nullable=False, index=True)  # parent phone
    parent_name = Column(String, nullable=False)
    dob         = Column(Date, nullable=True)
    address     = Column(Text, nullable=True)
    fees        = Column(Integer, default=1000)             # monthly fees ₹
    join_date   = Column(Date, server_default=func.current_date())
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    subjects    = relationship("StudentSubject", back_populates="student", cascade="all, delete-orphan")
    fees_records = relationship("FeeRecord", back_populates="student", cascade="all, delete-orphan")
    marks       = relationship("Mark", back_populates="student", cascade="all, delete-orphan")
    attendance  = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")


class StudentSubject(Base):
    __tablename__ = "student_subjects"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject    = Column(String, nullable=False)

    student    = relationship("Student", back_populates="subjects")


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id         = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    month      = Column(String, nullable=False)             # 'April 2025'
    amount     = Column(Integer, nullable=False)
    paid       = Column(Boolean, default=False)
    paid_date  = Column(Date, nullable=True)
    method     = Column(String, nullable=True)              # Cash / UPI / Bank Transfer
    notes      = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student    = relationship("Student", back_populates="fees_records")


class Mark(Base):
    __tablename__ = "marks"

    id         = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject    = Column(String, nullable=False)
    exam       = Column(String, nullable=False)             # 'Unit Test 1'
    max_marks  = Column(Integer, nullable=False)
    marks      = Column(Integer, nullable=False)
    exam_date  = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student    = relationship("Student", back_populates="marks")


class Attendance(Base):
    __tablename__ = "attendance"

    id         = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    date       = Column(Date, nullable=False)
    status     = Column(String, nullable=False)             # present / absent / holiday
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student    = relationship("Student", back_populates="attendance")


class Note(Base):
    __tablename__ = "notes"

    id          = Column(String, primary_key=True, default=gen_uuid)
    title       = Column(String, nullable=False)
    class_name  = Column(String, nullable=False)
    subject     = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_name   = Column(String, nullable=True)             # stored filename on disk
    file_path   = Column(String, nullable=True)             # full path
    file_type   = Column(String, default="pdf")
    downloads   = Column(Integer, default=0)
    upload_date = Column(Date, server_default=func.current_date())
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class OTPRecord(Base):
    __tablename__ = "otp_records"

    id         = Column(String, primary_key=True, default=gen_uuid)
    phone      = Column(String, nullable=False, index=True)
    otp_code   = Column(String, nullable=False)
    is_used    = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
