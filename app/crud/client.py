from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate

# CREATE
def create_client(db: Session, client: ClientCreate):
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# GET by id
def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

# GET by phone
def get_client_by_phone(db: Session, phone: str):
    return db.query(Client).filter(Client.phone == phone).first()

# GET all
def get_all_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Client).offset(skip).limit(limit).all()

# UPDATE
def update_client(db: Session, client_id: int, update: ClientUpdate):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        return None
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

# DELETE
def delete_client(db: Session, client_id: int):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        return None
    db.delete(db_client)
    db.commit()
    return db_client
