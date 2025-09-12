import requests
import random
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.client import Client as User
from app.core.security import create_access_token
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.schemas.auth import PhoneLogin
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class PhoneRequest(BaseModel):
    phone: str
    password: str

class VerifyOtpRequest(BaseModel):
    otp: str   # endi faqat OTP kiritiladi


# 🔹 OTP_STORE: vaqtinchalik xotira
OTP_STORE = {}

# 🔹 Eskiz config
ESKIIZ_LOGIN = os.getenv("ESKIIZ_LOGIN")
ESKIIZ_PASSWORD = os.getenv("ESKIIZ_PASSWORD")
AUTH_URL = "https://notify.eskiz.uz/api/auth/login"
SEND_URL = "https://notify.eskiz.uz/api/message/sms/send"

# 🔹 token cache
ESKIIZ_TOKEN = None

def get_token():
    global ESKIIZ_TOKEN
    if ESKIIZ_TOKEN:
        return ESKIIZ_TOKEN

    resp = requests.post(AUTH_URL, data={
        "email": ESKIIZ_LOGIN,
        "password": ESKIIZ_PASSWORD
    })
    if resp.status_code != 200:
        raise Exception("Eskiz login error: " + resp.text)

    ESKIIZ_TOKEN = resp.json()["data"]["token"]
    return ESKIIZ_TOKEN

def send_sms(phone: str, message: str):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "mobile_phone": phone.lstrip("+"),
        "message": message,
        "from": "4546"
    }
    resp = requests.post(SEND_URL, headers=headers, data=data)
    if resp.status_code != 200:
        raise Exception("Eskiz SMS error: " + resp.text)
    return resp.json()


# ====== OTP yuborish ======
@router.post("/send_otp")
def send_otp(data: PhoneRequest):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[data.phone] = {
        "otp": otp,
        "password": data.password,
        "created_at": datetime.utcnow()
    }

    message = f"Freya mobil ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {otp}"
    
    try:
        send_sms(data.phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "OTP yuborildi, 1 daqiqa davomida amal qiladi."}


# ====== OTP tasdiqlash ======
@router.post("/verify_otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    # 🔹 oxirgi yuborilgan OTP ni topamiz
    if not OTP_STORE:
        raise HTTPException(status_code=400, detail="OTP topilmadi")

    # oxirgi OTP ni olish
    phone, stored = list(OTP_STORE.items())[-1]

    expire_time = stored["created_at"] + timedelta(minutes=1)
    if datetime.utcnow() > expire_time:
        del OTP_STORE[phone]
        raise HTTPException(status_code=400, detail="OTP muddati tugagan")

    if stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Noto‘g‘ri OTP")

    # OTP ishlatildi -> o‘chirib tashlaymiz
    del OTP_STORE[phone]

    # 🔹 Foydalanuvchi mavjudligini tekshiramiz
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        hashed_password = get_password_hash(stored["password"])
        user = User(phone=phone, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


# ====== OTP qayta yuborish ======
@router.post("/resend_otp")
def resend_otp():
    if not OTP_STORE:
        raise HTTPException(status_code=400, detail="OTP yuborilmagan")

    phone, stored = list(OTP_STORE.items())[-1]

    # eski OTP ni o‘chirib tashlaymiz
    del OTP_STORE[phone]

    # yangi OTP yaratamiz
    otp = str(random.randint(100000, 999999))
    OTP_STORE[phone] = {
        "otp": otp,
        "password": stored["password"],
        "created_at": datetime.utcnow()
    }

    message = f"Freya mobil ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {otp}"
    try:
        send_sms(phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "Yangi OTP yuborildi, 1 daqiqa davomida amal qiladi."}


# ====== Parol xeshlash ======
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("$2a$") and not hashed_password.startswith("$2b$"):
        return plain_password == hashed_password
    return pwd_context.verify(plain_password, hashed_password)



# ====== Phone + Password LOGIN ======

@router.post("/login", summary="Login via phone & password")
def login_phone(data: PhoneLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Telefon raqam yoki parol noto‘g‘ri")

    if user.is_active is False:
        raise HTTPException(status_code=403, detail="Account bloklangan yoki faol emas")

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "is_premium": user.is_premium,
            "cashback_balance": user.cashback_balance,
        }
    }

