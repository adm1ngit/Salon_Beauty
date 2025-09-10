# app/schemas/salon.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class SalonBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

class SalonCreate(SalonBase):
    pass

class SalonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

class SalonOut(SalonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MasterBase(BaseModel):
    salon_id: int
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: str = Field(..., min_length=7, max_length=32)
    specialization: str = Field(..., min_length=2, max_length=100)  # masalan: tirnoq, massaj
    experience: Optional[int] = Field(default=None, ge=0, le=80)     # tajriba (yil)
    price: Optional[int] = Field(default=None, ge=0)                 # xizmat narxi (so'm)

class MasterCreate(MasterBase):
    pass

class MasterUpdate(BaseModel):
    salon_id: Optional[int] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone_number: Optional[str] = Field(None, min_length=7, max_length=32)
    specialization: Optional[str] = Field(None, min_length=2, max_length=100)
    experience: Optional[int] = Field(None, ge=0, le=80)
    price: Optional[int] = Field(None, ge=0)

class MasterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    salon_id: int
    full_name: str
    phone_number: str
    specialization: str
    experience: Optional[int]
    price: Optional[int]
    # Qo'shimcha: chiqishda salon haqida qisqa ma'lumot
    salon: Optional[SalonOut] = None