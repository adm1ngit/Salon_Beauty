from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str
    ENVIRONMENT: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 kun
    # CLICK
    CLICK_SERVICE_ID: int
    CLICK_MERCHANT_ID: int
    CLICK_SECRET_KEY: str
    CLICK_MERCHANT_USER_ID: int
    CLICK_API_URL: str

    # model_config = {
    #     "extra": "allow"  # Qo‘shimcha parametrlar ruxsat etiladi
    # }
    class Config:
        env_file = ".env"   # avtomatik ravishda .env fayldan o‘qiydi
        env_file_encoding = "utf-8"


settings = Settings()

if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
