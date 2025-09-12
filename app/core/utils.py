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
    otp: str

class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str


OTP_STORE = {}


# STEP 1. OTP yuborish
@router.post("/send_forgot_password_otp")
def send_forgot_password_otp(data: PhoneRequest, db: Session = Depends(get_db)):
    user = db.query(Client).filter(Client.phone == data.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="Bunday telefon raqam ro‘yxatdan o‘tmagan")

    OTP_STORE[data.phone] = {
        "otp": str(random.randint(100000, 999999)),
        "created_at": datetime.utcnow(),
        "expire_at": datetime.utcnow() + timedelta(minutes=1),
        "verified": False
    }

    message = f"Freya ilovasida parolni tiklash uchun tasdiqlash kodi: {{code}}"

    try:
        send_sms(data.phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "Parolni tiklash OTP yuborildi, 1 daqiqa davomida amal qiladi."}


# STEP 2. OTP ni tekshirish va reset_token yaratish (JWT)
@router.post("/verify_forgot_password_otp")
def verify_forgot_password_otp(data: VerifyOtpRequest):
    stored = OTP_STORE.get(data.phone)

    if not stored:
        raise HTTPException(status_code=400, detail="OTP topilmadi yoki qayta yuboring")

    if datetime.utcnow() > stored["expire_at"]:
        del OTP_STORE[data.phone]
        raise HTTPException(status_code=400, detail="OTP muddati tugagan, qayta yuboring.")

    if stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Noto‘g‘ri OTP")

    stored["verified"] = True
    return {"detail": "OTP muvaffaqiyatli tasdiqlandi."}


# STEP 3. Yangi parol o‘rnatish (JWT reset_token orqali)
@router.post("/reset_password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    # OTP_STORE dan verified userni topamiz
    verified_phone = None
    for phone, info in OTP_STORE.items():
        if info.get("verified"):
            # 🔹 Expire tekshirishni reset bosqichida ham qilamiz
            if datetime.utcnow() > info["expire_at"]:
                del OTP_STORE[phone]
                raise HTTPException(status_code=400, detail="OTP muddati tugagan, qayta yuboring.")
            verified_phone = phone
            break

    if not verified_phone:
        raise HTTPException(status_code=400, detail="Avval OTP ni tasdiqlash kerak")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Parollar mos emas")

    user = db.query(Client).filter(Client.phone == verified_phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    # 🔑 Parolni yangilaymiz
    user.password = get_password_hash(data.new_password)
    db.commit()

    # OTP ishlatilib bo‘ldi → o‘chiramiz
    del OTP_STORE[verified_phone]

    return {"detail": "Parol muvaffaqiyatli yangilandi"}
