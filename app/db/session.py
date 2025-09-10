from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models import client, salon, service, booking, review, chat
from typing import Generator

# 🔹 Engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 🔹 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
