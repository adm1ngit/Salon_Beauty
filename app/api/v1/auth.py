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
from datetime import datetime
from app.schemas.auth import PhoneLogin
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class PhoneRequest(BaseModel):
    phone: str
    password: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

OTP_STORE = {}

# 🔹 Eskiz config .env dan
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


@router.post("/send_otp")
def send_otp(data: PhoneRequest):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[data.phone] = {"otp": otp, "password": data.password}  # 🔹 parolni vaqtincha saqlaymiz

    message = f"Freya mobil ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {otp}"
    
    try:
        send_sms(data.phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "OTP yuborildi"}


@router.post("/verify_otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    stored = OTP_STORE.get(data.phone)
    if not stored or stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        hashed_password = get_password_hash(stored["password"])
        user = User(phone=data.phone, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


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
