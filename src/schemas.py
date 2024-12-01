from datetime import datetime
from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List
import re
from enum import Enum

TRANSACTION_STATUSES = ["success", "failed", "pending"]

class TransactionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class TransactionBase(BaseModel):
    transaction_id: str = Field(..., min_length=8, max_length=50)
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    receiver_merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    timestamp: datetime
    amount: float = Field(..., gt=0, lt=1000000)
    payment_method: str = Field(..., min_length=3, max_length=50)
    status: TransactionStatus
    product_category: str
    platform: str
    customer_location: str = Field(..., min_length=2, max_length=100)
    customer_id: str = Field(..., min_length=8)
    device_id: str = Field(..., min_length=8)
    velocity_flag: bool = False
    amount_flag: bool = False
    time_flag: bool = False
    device_flag: bool = False

class Transaction(TransactionBase):
    id: int
    
    class Config:
        from_attributes = True

class MerchantBase(BaseModel): 
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    business_name: str = Field(..., min_length=5, max_length=100)
    business_type: str = Field(..., min_length=3)
    registration_date: datetime
    business_model: str = Field(..., pattern="^(Online|Offline|Hybrid)$")
    product_category: str
    average_ticket_size: float = Field(..., gt=0)
    gst_status: bool
    epfo_registered: bool
    registered_address: str = Field(..., min_length=10, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    reported_revenue: float = Field(..., gt=0)
    employee_count: int = Field(..., gt=0, lt=1000000)
    bank_account: str = Field(..., min_length=8, max_length=20)

    class Config:
        from_attributes = True

class Merchant(MerchantBase):
    id: int
    transactions: List[Transaction] = []
    
    class Config:
        from_attributes = True

class RiskMetricsBase(BaseModel):
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    timestamp: datetime
    late_night_score: float = Field(..., ge=0, le=1)
    sudden_spike_score: float = Field(..., ge=0, le=1)
    velocity_abuse_score: float = Field(..., ge=0, le=1)
    device_switching_score: float = Field(..., ge=0, le=1)
    location_hopping_score: float = Field(..., ge=0, le=1)
    payment_cycling_score: float = Field(..., ge=0, le=1)
    round_amount_score: float = Field(..., ge=0, le=1)
    customer_concentration_score: float = Field(..., ge=0, le=1)
    composite_risk_score: float = Field(..., ge=0, le=1)

    class Config:
        from_attributes = True

class TransactionSummaryBase(BaseModel):
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    date: datetime
    txn_count: int = Field(..., ge=0)
    total_volume: float = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0)
    max_amount: float = Field(..., ge=0)
    min_amount: float = Field(..., ge=0)
    unique_customers: int = Field(..., ge=0)
    unique_payment_methods: int = Field(..., ge=0)

    class Config:
        from_attributes = True
