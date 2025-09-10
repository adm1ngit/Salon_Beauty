from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# 🔹 Engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 🔹 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Import models here so Alembic sees them
from app.models import client, salon, service, booking, review, chat

# 🔹 FastAPI dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
