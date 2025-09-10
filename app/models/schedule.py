from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"))
    day = Column(String, nullable=False)      # masalan: dushanba
    start_time = Column(String, nullable=False)  # 09:00
    end_time = Column(String, nullable=False)    # 18:00

    master = relationship("Master", back_populates="schedules")
