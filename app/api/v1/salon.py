# app/api/v1/salon.py

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# ✅ to'g'ri import
from app.core.security import get_db
# ✅ token tekshiruvi (sendagi security.py ichida bo'lishi kerak)
from app.core.security import get_current_user

# Schemas: barchasi bitta schemas/salon.py ichida
from app.schemas.salon import (
    SalonCreate, SalonUpdate, SalonOut,
    MasterCreate, MasterUpdate, MasterOut,
)

# CRUD: barchasi bitta crud/crud_salon.py ichida
from app.crud.crud_salon import (
    create_salon, get_salon, update_salon, delete_salon, list_salons,
    create_master, get_master, update_master, delete_master, list_masters,
)

# 🔐 Bu router ichidagi BARCHA endpointlar token talab qiladi
router = APIRouter(dependencies=[Depends(get_current_user)])

# =========================
#           SALONS
# =========================
@router.post("/salons/", response_model=SalonOut, status_code=201)
def create_salon_endpoint(data: SalonCreate, db: Session = Depends(get_db)):
    return create_salon(db, data)

@router.get("/salons/{salon_id}", response_model=SalonOut)
def get_salon_endpoint(salon_id: int, db: Session = Depends(get_db)):
    obj = get_salon(db, salon_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Salon not found")
    return obj

@router.put("/salons/{salon_id}", response_model=SalonOut)
@router.patch("/salons/{salon_id}", response_model=SalonOut)
def update_salon_endpoint(salon_id: int, data: SalonUpdate, db: Session = Depends(get_db)):
    obj = update_salon(db, salon_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Salon not found")
    return obj

@router.delete("/salons/{salon_id}", status_code=204)
def delete_salon_endpoint(salon_id: int, db: Session = Depends(get_db)):
    ok = delete_salon(db, salon_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Salon not found")
    return None

@router.get("/salons/", response_model=Dict[str, Any])
def list_salons_endpoint(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Name/address qidiruv"),
    city: Optional[str] = None,
    district: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
):
    rows, total = list_salons(db, q=q, city=city, district=district, offset=offset, limit=limit)
    return {"total": total, "items": [SalonOut.model_validate(r) for r in rows]}

# =========================
#           MASTERS
# =========================
@router.post("/masters/", response_model=MasterOut, status_code=201)
def create_master_endpoint(data: MasterCreate, db: Session = Depends(get_db)):
    try:
        return create_master(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/masters/{master_id}", response_model=MasterOut)
def get_master_endpoint(master_id: int, db: Session = Depends(get_db)):
    obj = get_master(db, master_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Master not found")
    return obj

@router.put("/masters/{master_id}", response_model=MasterOut)
@router.patch("/masters/{master_id}", response_model=MasterOut)
def update_master_endpoint(master_id: int, data: MasterUpdate, db: Session = Depends(get_db)):
    try:
        obj = update_master(db, master_id, data)
        if not obj:
            raise HTTPException(status_code=404, detail="Master not found")
        return obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/masters/{master_id}", status_code=204)
def delete_master_endpoint(master_id: int, db: Session = Depends(get_db)):
    ok = delete_master(db, master_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Master not found")
    return None

@router.get("/masters/", response_model=Dict[str, Any])
def list_masters_endpoint(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Full name/phone/specialization qidiruv"),
    salon_id: Optional[int] = None,
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    min_experience: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    order_by: Optional[str] = Query(None, pattern=r"^-?(price|experience)$"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
):
    rows, total = list_masters(
        db,
        q=q,
        salon_id=salon_id,
        specialization=specialization,
        city=city,
        district=district,
        min_experience=min_experience,
        max_price=max_price,
        order_by=order_by,
        offset=offset,
        limit=limit,
    )
    return {"total": total, "items": [MasterOut.model_validate(r) for r in rows]}
