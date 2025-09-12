import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    password = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=True)
    profile_picture = Column(String, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    district = Column(String, nullable=True)
    city = Column(String, nullable=True)
    interests = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    cashback_balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="client")
    subscriptions = relationship("Subscription", back_populates="client", cascade="all, delete-orphan")
