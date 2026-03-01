from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from src.database.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    # Core transaction info
    transaction_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)
    merchant_category = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_status = Column(String(20), nullable=False, default="success")
    
    # Sender info
    sender_age_group = Column(String(20), nullable=False, index=True)
    sender_state = Column(String(50), nullable=False, index=True)
    sender_bank = Column(String(100), nullable=False)
    
    # Receiver info
    receiver_age_group = Column(String(20), nullable=False, index=True)
    receiver_bank = Column(String(100), nullable=False)
    
    # Device & Network
    device_type = Column(String(20), nullable=False)
    network_type = Column(String(20), nullable=False)
    
    # Risk indicators
    fraud_flag = Column(Boolean, default=False, index=True)
    
    # Temporal features
    hour_of_day = Column(Integer, nullable=False)  # 0-23
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday-Sunday)
    is_weekend = Column(Boolean, default=False, index=True)
    
    class Config:
        from_attributes = True
