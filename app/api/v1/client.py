from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.client import ClientUpdate, ClientResponse
from app.crud import client as crud_client
from app.core.security import get_current_user
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from app.schemas.client import ClientResponse
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    password: Optional[str] = None

class UpdateClientResponse(BaseModel):
    phone: str
    name: Optional[str]
    profile_picture: Optional[str]

    class Config:
        from_attributes = True

@router.put("/profile", response_model=UpdateClientResponse)
def update_profile(
    update: UpdateClientRequest,
    db: Session = Depends(get_db),
    current_user: ClientResponse = Depends(get_current_user)
):
    user = db.query(UpdateClientRequest).filter(UpdateClientRequest.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ma'lumotlarni yangilash
    if update.name is not None:
        user.name = update.name

    if update.profile_picture is not None:
        user.profile_picture = update.profile_picture

    if update.password is not None:
        user.password = pwd_context.hash(update.password)

    db.commit()
    db.refresh(user)

    return user

# READ all
@router.get("/", response_model=List[ClientResponse])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_client.get_all_clients(db, skip=skip, limit=limit)


# READ by id
@router.get("/{client_id}", response_model=ClientResponse)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_client = crud_client.get_client(db, client_id=client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client


# ✅ UPDATE PROFILE (faqat o‘zini yangilash)
@router.put("/me", response_model=ClientResponse)
def update_profile(
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_client = crud_client.update_client(db, client_id=current_user.id, update=client)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client


# DELETE (agar kerak bo‘lsa, faqat superadmin ishlatadi)
@router.delete("/{client_id}", response_model=ClientResponse)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_client = crud_client.delete_client(db, client_id=client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client