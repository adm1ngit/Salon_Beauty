from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubscriptionBase(BaseModel):
    plan_name: str = "Premium"
    price: float = 9900.0
    cashback_enabled: bool = True
    active: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SubscriptionCreate(BaseModel):
    client_id : int


class SubscriptionUpdate(BaseModel):
    active: Optional[bool] = None
    end_date: Optional[datetime] = None


class SubscriptionInDBBase(SubscriptionBase):
    id: int
    client_id : int

    class Config:
        orm_mode = True


class SubscriptionResponse(SubscriptionInDBBase):
    pass
