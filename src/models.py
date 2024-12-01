from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.types import JSON
from sqlalchemy.schema import Index

Base = declarative_base()

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, unique=True, index=True)
    business_name = Column(String)
    business_type = Column(String)
    registration_date = Column(DateTime)
    business_model = Column(String)
    product_category = Column(String)
    average_ticket_size = Column(Float)
    gst_status = Column(Boolean)
    epfo_registered = Column(Boolean)
    registered_address = Column(String)
    city = Column(String)
    state = Column(String)
    reported_revenue = Column(Float)
    employee_count = Column(Integer)
    bank_account = Column(String)
    
    transactions = relationship("Transaction", back_populates="merchant")
    risk_metrics = relationship("RiskMetrics", back_populates="merchant")
    transaction_summaries = relationship("TransactionSummary", back_populates="merchant")
    timeline_events = relationship("TimelineEvent", back_populates="merchant")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"))
    receiver_merchant_id = Column(String)
    timestamp = Column(DateTime)
    amount = Column(Float)
    payment_method = Column(String)
    status = Column(String)
    product_category = Column(String)
    platform = Column(String)
    customer_location = Column(String)
    customer_id = Column(String)
    device_id = Column(String)
    
    # Risk flags
    velocity_flag = Column(Boolean, default=False)
    amount_flag = Column(Boolean, default=False)
    time_flag = Column(Boolean, default=False)
    device_flag = Column(Boolean, default=False)
    
    merchant = relationship("Merchant", back_populates="transactions")

class RiskMetrics(Base):
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Individual risk scores
    late_night_score = Column(Float)
    sudden_spike_score = Column(Float)
    velocity_abuse_score = Column(Float)
    device_switching_score = Column(Float)
    location_hopping_score = Column(Float)
    payment_cycling_score = Column(Float)
    round_amount_score = Column(Float)
    customer_concentration_score = Column(Float)
    
    # Composite score
    composite_risk_score = Column(Float)
    
    # Relationship
    merchant = relationship("Merchant", back_populates="risk_metrics")

class TransactionSummary(Base):
    __tablename__ = "transaction_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"))
    date = Column(DateTime, index=True)
    txn_count = Column(Integer)
    total_volume = Column(Float)
    avg_amount = Column(Float)
    max_amount = Column(Float)
    min_amount = Column(Float)
    unique_customers = Column(Integer)
    unique_payment_methods = Column(Integer)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="transaction_summaries")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"), index=True)
    event_type = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    details = Column(JSON)
    severity = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_merchant_timestamp', 'merchant_id', 'timestamp'),
    )
    
    # Relationship
    merchant = relationship("Merchant", back_populates="timeline_events")