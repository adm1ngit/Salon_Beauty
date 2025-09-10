from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"

# ---- CREATE ----
class ClientCreate(BaseModel):
    phone: str
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    district: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None

# ---- UPDATE ----
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    district: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    cashback_balance: Optional[int] = None
    last_login: Optional[datetime] = None

# ---- RESPONSE ----
class ClientResponse(BaseModel):
    id: int
    phone: str
    name: Optional[str]
    birth_date: Optional[date]
    gender: Optional[GenderEnum]
    district: Optional[str]
    city: Optional[str]
    interests: Optional[List[str]]
    is_active: bool
    is_premium: bool
    cashback_balance: int
    created_at: datetime
    last_login: datetime

    class Config:
        orm_mode = True
