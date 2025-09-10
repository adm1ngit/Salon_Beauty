from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.crud.crud_subscription import subscription_crud
from app.core.security import get_current_user
from app.models.client import Client
    
router = APIRouter()

@router.post("/premium", response_model=SubscriptionResponse)
def create_premium_subscription(
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),
):
    if current_user.is_premium:
        raise HTTPException(status_code=400, detail="Premium allaqachon aktiv")

    obj_in = SubscriptionCreate(client_id=current_user.id)
    new_subscription = subscription_crud.create(db, obj_in)

    # 🔹 Premium flagni client jadvalida update qilamiz
    current_user.is_premium = True
    db.commit()
    db.refresh(current_user)

    return new_subscription


@router.get("/premium/check", response_model=dict)
def check_premium_status(current_user: Client = Depends(get_current_user)):
    return {"is_premium": current_user.is_premium}
