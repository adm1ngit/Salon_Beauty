from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models here so Alembic sees them
from app.models import client, salon, service, booking, review, chat

