import httpx
import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from app import models

load_dotenv()

FAST2SMS_API_KEY   = os.getenv("FAST2SMS_API_KEY", "")
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", 10))


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_otp_fast2sms(phone: str, otp: str) -> dict:
    # DEV MODE
    if not FAST2SMS_API_KEY or FAST2SMS_API_KEY == "your_fast2sms_api_key_here":
        print("\n" + "="*45)
        print(f"  📱 DEV MODE — OTP for {phone} : {otp}")
        print("="*45 + "\n")
        return {"status": "dev_mode", "otp": otp}

    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type":  "application/json",
    }
    payload = {
        "route":    "q",
        "message":  f"Your Shri Ji Classes OTP is {otp}. Valid for {OTP_EXPIRE_MINUTES} minutes. Do not share with anyone.",
        "language": "english",
        "flash":    0,
        "numbers":  phone,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()
            if not data.get("return"):
                error_msg = data.get("message", [])
                if isinstance(error_msg, list):
                    error_msg = ", ".join(error_msg)
                raise Exception(f"Fast2SMS error: {error_msg}")
            print(f"✅ OTP sent to {phone}")
            return data
    except httpx.TimeoutException:
        raise Exception("Fast2SMS timed out. Check internet connection.")


def save_otp(db: Session, phone: str, otp: str):
    db.query(models.OTPRecord).filter(
        models.OTPRecord.phone   == phone,
        models.OTPRecord.is_used == False,
    ).update({"is_used": True})

    record = models.OTPRecord(
        phone      = phone,
        otp_code   = otp,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
    )
    db.add(record)
    db.commit()
    return record


def verify_otp(db: Session, phone: str, otp: str) -> bool:
    record = db.query(models.OTPRecord).filter(
        models.OTPRecord.phone      == phone,
        models.OTPRecord.otp_code   == otp,
        models.OTPRecord.is_used    == False,
        models.OTPRecord.expires_at >  datetime.now(timezone.utc),
    ).first()

    if not record:
        return False

    record.is_used = True
    db.commit()
    return True
