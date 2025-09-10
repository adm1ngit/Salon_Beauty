import hashlib
import requests
from app.core.config import settings


class ClickService:
    def __init__(self):
        self.service_id = settings.CLICK_SERVICE_ID
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.secret_key = settings.CLICK_SECRET_KEY
        self.merchant_user_id = settings.CLICK_MERCHANT_USER_ID
        self.api_url = settings.CLICK_API_URL

    def generate_sign(self, params: dict) -> str:
        """
        Click sign generatsiya qilish (hashlash)
        """
        sign_string = ":".join([
            str(params["click_trans_id"]),
            str(params["service_id"]),
            self.secret_key,
            str(params["merchant_trans_id"]),
            str(params["amount"]),
            str(params["action"]),
            str(params["sign_time"])
        ])
        return hashlib.md5(sign_string.encode()).hexdigest()

    def create_payment(self, user_id: int, amount: float = 9900):
        """
        To‘lov yaratish (foydalanuvchi uchun)
        """
        payload = {
            "service_id": self.service_id,
            "merchant_id": self.merchant_id,
            "merchant_user_id": self.merchant_user_id,
            "merchant_trans_id": f"{user_id}",   # har bir foydalanuvchiga unikal ID
            "amount": amount,
            "action": 0,
            "sign_time": "2025-09-04 12:00:00",  # real vaqt qo‘yiladi
        }

        # Sign generatsiya
        payload["sign_string"] = self.generate_sign({
            "click_trans_id": 0,
            "service_id": self.service_id,
            "merchant_trans_id": payload["merchant_trans_id"],
            "amount": payload["amount"],
            "action": payload["action"],
            "sign_time": payload["sign_time"],
        })

        response = requests.post(f"{self.api_url}/init-payment", json=payload)

        if response.status_code != 200:
            raise Exception(f"Click API error: {response.text}")

        return response.json()
