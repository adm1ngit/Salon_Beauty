from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class CRUDSubscription:
    def create(self, db: Session, obj_in: SubscriptionCreate) -> Subscription:
        subscription = Subscription(
            client_id =obj_in.client_id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            active=True
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    def get_by_user(self, db: Session, client_id : int):
        return db.query(Subscription).filter(Subscription.client_id  == client_id ).first()

    def update(self, db: Session, db_obj: Subscription, obj_in: SubscriptionUpdate):
        if obj_in.active is not None:
            db_obj.active = obj_in.active
        if obj_in.end_date is not None:
            db_obj.end_date = obj_in.end_date
        db.commit()
        db.refresh(db_obj)
        return db_obj


subscription_crud = CRUDSubscription()
