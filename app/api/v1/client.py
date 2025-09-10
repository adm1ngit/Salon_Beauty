from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.client import ClientUpdate, ClientResponse
from app.crud import client as crud_client
from app.core.security import get_current_user

router = APIRouter()


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
