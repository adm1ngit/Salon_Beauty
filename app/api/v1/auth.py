import requests
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.client import Client as User
from app.core.security import create_access_token
from passlib.context import CryptContext
from datetime import datetime
from app.schemas.auth import EmailLogin


router = APIRouter()

class PhoneRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

OTP_STORE = {}

# 🔹 Eskiiz config
ESKIIZ_LOGIN = "fayzullindmr@gmail.com"
ESKIIZ_PASSWORD = "rlPJjmkaqRvZshRoNpcIiCFtC5GiNzI7k7YNe8fs"
AUTH_URL = "https://notify.eskiz.uz/api/auth/login"
SEND_URL = "https://notify.eskiz.uz/api/message/sms/send"

# 🔹 tokenni cache qilib olamiz
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
        "mobile_phone": phone.lstrip("+"),  # +998901234567 → 998901234567
        "message": message,
        "from": "4546"  # Eskiz bilan kelishilgan qisqa nomer bo‘lishi kerak
    }
    resp = requests.post(SEND_URL, headers=headers, data=data)
    if resp.status_code != 200:
        raise Exception("Eskiz SMS error: " + resp.text)
    return resp.json()


@router.post("/send_otp")
def send_otp(data: PhoneRequest):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[data.phone] = otp

    # 🔹 Tasdiqlangan matinga moslab SMS yuborish
    message = f"Freya mobil ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {otp}"
    
    try:
        send_sms(data.phone, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": "OTP yuborildi"}


@router.post("/verify_otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    otp = OTP_STORE.get(data.phone)
    if otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(phone=data.phone)
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
    # Eski tizimda plain saqlangan bo'lsa, vaqtincha fallback
    if not hashed_password.startswith("$2a$") and not hashed_password.startswith("$2b$"):
        return plain_password == hashed_password
    return pwd_context.verify(plain_password, hashed_password)

# ====== Email + Password LOGIN ======
@router.post("/login", summary="Login via email & password")
def login_email(data: EmailLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Email yoki parol noto‘g‘ri")

    if user.is_active is False:
        raise HTTPException(status_code=403, detail="Account bloklangan yoki faol emas")

    # last_login ni yangilab qo'yamiz
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
            "email": user.email,
            "phone": user.phone,
            "is_premium": user.is_premium,
            "cashback_balance": user.cashback_balance,
        }
    }