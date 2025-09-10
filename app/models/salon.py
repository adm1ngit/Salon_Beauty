from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Salon(Base):
    __tablename__ = "salons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)

    masters = relationship("Master", back_populates="salon")


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    specialization = Column(String, nullable=False)  # masalan: tirnoq, massaj
    experience = Column(Integer, nullable=True)      # tajriba yillari
    price = Column(Integer, nullable=True)           # xizmat narxi

    salon = relationship("Salon", back_populates="masters")
    schedules = relationship("Schedule", back_populates="master")
    bookings = relationship("Booking", back_populates="master")

 