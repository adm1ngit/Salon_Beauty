from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


# 🔹 faqat create qilishda ishlatiladi
class BookingCreate(BaseModel):
    master_id: int
    service: str
    start_time: datetime
    end_time: datetime


# 🔹 update uchun
class BookingUpdate(BaseModel):
    service: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None


# 🔹 umumiy schema (response uchun)
class BookingBase(BaseModel):
    id: int
    client_id: int
    master_id: int
    service: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus

    class Config:
        orm_mode = True
