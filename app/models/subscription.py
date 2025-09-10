from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    plan_name = Column(String, default="Premium")
    price = Column(Float, default=9900.0)
    cashback_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)

    client = relationship("Client", back_populates="subscriptions")

    def activate(self):
        """Premiumni 1 oyga aktiv qiladi"""
        self.active = True
        self.start_date = datetime.utcnow()
        self.end_date = datetime.utcnow() + timedelta(days=30)
