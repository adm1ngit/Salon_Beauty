from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import get_current_user
import hashlib
import httpx
from app.models.client import Client

router = APIRouter()


# 🔹 1. Premium obuna yaratish
@router.post("/premium")
async def create_premium_subscription(
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),  # Client obyekti qaytadi
):
    client_id = current_user.id   # ✅ Bu joyda .get("sub") emas, balki .id

    # Click payment link yasash
    payment_url = (
        f"https://my.click.uz/services/pay?"
        f"service_id={settings.CLICK_SERVICE_ID}"
        f"&merchant_id={settings.CLICK_MERCHANT_ID}"
        f"&amount=9900"
        f"&transaction_param=user_{client_id}"
        f"&return_url=https://your-frontend.uz/payment-success"
    )

    return {"payment_url": payment_url}


# 🔹 2. Callback (faqat Click chaqiradi!)
def check_sign(data: dict) -> bool:
    sign_str = (
        f"{data['click_trans_id']}"
        f"{data['service_id']}"
        f"{settings.CLICK_SECRET_KEY}"
        f"{data['merchant_trans_id']}"
        f"{data['amount']}"
        f"{data['action']}"
        f"{data['sign_time']}"
    )
    return hashlib.md5(sign_str.encode()).hexdigest() == data['sign_string']


@router.post("/click/callback")
async def click_callback(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    data = dict(form_data)

    if not check_sign(data):
        return {"error_code": -406, "error_note": "SIGN CHECK FAILED"}

    if int(data.get("error", 0)) != 0:
        return {"error_code": data["error"], "error_note": data["error_note"]}

    # 🔹 merchant_trans_id orqali foydalanuvchini aniqlash
    merchant_trans_id = data.get("merchant_trans_id") or data.get("transaction_param")
    if not merchant_trans_id or not merchant_trans_id.startswith("user_"):
        return {"error_code": -5, "error_note": "Invalid transaction_param"}

    client_id = int(merchant_trans_id.split("_")[1])

    # 🔹 Foydalanuvchini premium qilish
    from app.models.client import Client
    user = db.query(Client).filter(Client.id == client_id).first()
    if user:
        user.is_premium = True
        db.commit()
        db.refresh(user)

    return {"error_code": 0, "error_note": "Success"}

