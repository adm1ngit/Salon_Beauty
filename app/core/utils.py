from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
from app.db.session import get_db
from app.models.client import Client
from app.api.v1.auth import get_password_hash
from app.api.v1.auth import send_sms
from jose import jwt
from app.core.config import settings

router = APIRouter()

class PhoneRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

class ResetPasswordRequest(BaseModel):
    new_password: str
    token: str


# 🔹 Temporary OTP cache (faqat 1 daqiqa)
OTP_STORE = {}


# STEP 1. OTP yuborish
@router.post("/send_otp")
def send_forgot_password_otp(data: PhoneRequest, db: Session = Depends(get_db)):
    user = db.query(Client).filter(Client.phone == data.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="Bunday telefon raqam ro‘yxatdan o‘tmagan")

    otp = str(random.randint(100000, 999999))
    OTP_STORE[data.phone] = {
        "otp": otp,
        "created_at": datetime.utcnow(),
    }

    message = f"Freya ilovasida parolni tiklash uchun tasdiqlash kodi: {otp}"
    try:
        send_sms(data.phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "Parolni tiklash OTP yuborildi, 1 daqiqa davomida amal qiladi."}


# STEP 2. OTP ni tekshirish va reset_token yaratish (JWT)
@router.post("/verify_otp")
def verify_forgot_password_otp(data: VerifyOtpRequest):
    stored = OTP_STORE.get(data.phone)

    if not stored:
        raise HTTPException(status_code=400, detail="OTP topilmadi yoki qayta yuboring")

    expire_time = stored["created_at"] + timedelta(minutes=1)
    if datetime.utcnow() > expire_time:
        del OTP_STORE[data.phone]
        raise HTTPException(status_code=400, detail="OTP muddati tugagan")

    if stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Noto‘g‘ri OTP")

    # ✅ OTP tug‘ri → JWT reset_token yaratamiz
    reset_payload = {
        "sub": data.phone,
        "purpose": "forgot_password",
        "exp": datetime.utcnow() + timedelta(minutes=5)  # 5 daqiqa amal qiladi
    }
    reset_token = jwt.encode(reset_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # OTP ni o‘chiramiz (faqat token qolsin)
    del OTP_STORE[data.phone]

    return {"reset_token": reset_token, "detail": "OTP tasdiqlandi. Endi parolni yangilash mumkin."}


# STEP 3. Yangi parol o‘rnatish (JWT reset_token orqali)
@router.post("/reset_password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone = payload.get("sub")
        purpose = payload.get("purpose")

        if purpose != "forgot_password":
            raise HTTPException(status_code=400, detail="Noto‘g‘ri token")

    except Exception:
        raise HTTPException(status_code=400, detail="Reset token yaroqsiz yoki muddati tugagan")

    user = db.query(Client).filter(Client.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    user.password = get_password_hash(data.new_password)
    db.add(user)
    db.commit()

    return {"detail": "Parol muvaffaqiyatli yangilandi"}
