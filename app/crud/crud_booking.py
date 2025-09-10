# app/crud/crud_booking.py
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate
from app.db.session import SessionLocal

class CRUDBooking:
    def __init__(self, db):
        self.db = db

    def create(self, booking: BookingCreate):
        db_booking = Booking(**booking.dict())
        self.db.add(db_booking)
        self.db.commit()
        self.db.refresh(db_booking)
        return db_booking

    def get(self, booking_id: int):
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def get_all(self):
        return self.db.query(Booking).all()

    def update(self, booking_id: int, booking: BookingUpdate):
        db_booking = self.get(booking_id)
        if not db_booking:
            return None
        for field, value in booking.dict(exclude_unset=True).items():
            setattr(db_booking, field, value)
        self.db.commit()
        self.db.refresh(db_booking)
        return db_booking

    def delete(self, booking_id: int):
        db_booking = self.get(booking_id)
        if not db_booking:
            return None
        self.db.delete(db_booking)
        self.db.commit()
        return db_booking


# 🔑 shu yerda booking_crud ni yaratib qo‘yamiz
db = SessionLocal()
booking_crud = CRUDBooking(db)
