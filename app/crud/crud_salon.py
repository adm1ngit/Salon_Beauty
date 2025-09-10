from typing import Optional, List, Tuple   # type hint uchun
from sqlalchemy.orm import Session, joinedload   # db session va relationship preload
from sqlalchemy import select, func, or_, and_   # SQLAlchemy query qurish
from app.models.salon import Salon, Master       # ORM modellaring
from app.schemas.salon import SalonCreate, SalonUpdate
from app.schemas.salon import MasterCreate, MasterUpdate


# ---- Salon ----
def create_salon(db: Session, data: SalonCreate) -> Salon:
    obj = Salon(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_salon(db: Session, salon_id: int) -> Optional[Salon]:
    return db.get(Salon, salon_id)

def update_salon(db: Session, salon_id: int, data: SalonUpdate) -> Optional[Salon]:
    obj = db.get(Salon, salon_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_salon(db: Session, salon_id: int) -> bool:
    obj = db.get(Salon, salon_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def list_salons(
    db: Session,
    q: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> Tuple[List[Salon], int]:
    stmt = select(Salon)
    cnt = select(func.count(Salon.id))

    if q:
        like = f"%{q.strip()}%"
        cond = or_(Salon.name.ilike(like), Salon.address.ilike(like))
        stmt = stmt.where(cond)
        cnt = cnt.where(cond)

    if city:
        stmt = stmt.where(Salon.city == city)
        cnt = cnt.where(Salon.city == city)

    if district:
        stmt = stmt.where(Salon.district == district)
        cnt = cnt.where(Salon.district == district)

    total = db.execute(cnt).scalar() or 0
    rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    return rows, total

# ---- Master ----
def _phone_exists(db: Session, phone: str, exclude_id: Optional[int] = None) -> bool:
    stmt = select(func.count(Master.id)).where(Master.phone_number == phone)
    if exclude_id:
        stmt = stmt.where(Master.id != exclude_id)
    return (db.execute(stmt).scalar() or 0) > 0

def create_master(db: Session, data: MasterCreate) -> Master:
    if not db.get(Salon, data.salon_id):
        raise ValueError("Salon not found")
    if _phone_exists(db, data.phone_number):
        raise ValueError("Phone number already exists")
    obj = Master(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_master(db: Session, master_id: int) -> Optional[Master]:
    return db.execute(
        select(Master).options(joinedload(Master.salon)).where(Master.id == master_id)
    ).scalar_one_or_none()

def update_master(db: Session, master_id: int, data: MasterUpdate) -> Optional[Master]:
    obj = db.get(Master, master_id)
    if not obj:
        return None

    payload = data.model_dump(exclude_unset=True)

    if "salon_id" in payload and payload["salon_id"] is not None:
        if not db.get(Salon, payload["salon_id"]):
            raise ValueError("Salon not found")

    new_phone = payload.get("phone_number")
    if new_phone and _phone_exists(db, new_phone, exclude_id=master_id):
        raise ValueError("Phone number already exists")

    for k, v in payload.items():
        setattr(obj, k, v)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_master(db: Session, master_id: int) -> bool:
    obj = db.get(Master, master_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def list_masters(
    db: Session,
    q: Optional[str] = None,
    salon_id: Optional[int] = None,
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_price: Optional[int] = None,
    order_by: Optional[str] = None,  # "price", "-price", "experience", "-experience"
    offset: int = 0,
    limit: int = 20,
) -> Tuple[List[Master], int]:
    stmt = select(Master).options(joinedload(Master.salon))
    cnt = select(func.count(Master.id))
    conds = []

    if q:
        like = f"%{q.strip()}%"
        conds.append(or_(
            Master.full_name.ilike(like),
            Master.phone_number.ilike(like),
            Master.specialization.ilike(like)
        ))

    if salon_id:
        conds.append(Master.salon_id == salon_id)
    if specialization:
        conds.append(Master.specialization == specialization)
    if min_experience is not None:
        conds.append(Master.experience >= min_experience)
    if max_price is not None:
        conds.append(or_(Master.price <= max_price, Master.price.is_(None)))

    if city or district:
        stmt = stmt.join(Salon, Master.salon_id == Salon.id)
        cnt = cnt.join(Salon, Master.salon_id == Salon.id)
        if city:
            conds.append(Salon.city == city)
        if district:
            conds.append(Salon.district == district)

    if conds:
        stmt = stmt.where(and_(*conds))
        cnt = cnt.where(and_(*conds))

    if order_by:
        mapping = {
            "price": Master.price.asc(),
            "-price": Master.price.desc(),
            "experience": Master.experience.asc(),
            "-experience": Master.experience.desc(),
        }
        if order_by in mapping:
            stmt = stmt.order_by(mapping[order_by])

    total = db.execute(cnt).scalar() or 0
    rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    return rows, total