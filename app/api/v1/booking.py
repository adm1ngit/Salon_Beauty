from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingUpdate, BookingBase
from app.crud.crud_booking import booking_crud
from app.core.security import get_current_user  # token tekshiruv

router = APIRouter()


@router.post("/", response_model=BookingBase)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 🔑 token orqali
):
    # Token ichidan client_id yoki phone olish
    client_id = current_user.get("sub")  
    return booking_crud.create(db, obj_in=booking_in, client_id=client_id)


@router.get("/{booking_id}", response_model=BookingBase)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    booking = booking_crud.get(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/", response_model=List[BookingBase])
def get_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return booking_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{booking_id}", response_model=BookingBase)
def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    booking = booking_crud.get(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_crud.update(db, db_obj=booking, obj_in=booking_in)


@router.delete("/{booking_id}", response_model=BookingBase)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    booking = booking_crud.remove(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
