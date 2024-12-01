import random
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from faker import Faker
from pydantic import BaseModel, Field, validator, constr, ValidationError
from typing import Optional, List
import re
from .schemas import TRANSACTION_STATUSES
import logging

logger = logging.getLogger(__name__)

# Initialize Faker for generating realistic data
fake = Faker()

# Predefined lists for realistic data generation
BUSINESS_TYPES = [
    "Electronics", "Fashion", "Food & Beverage", "Retail", 
    "Technology", "Services", "Healthcare", "Education",
    "Entertainment", "Automotive", "Real Estate", "Construction",
    "Manufacturing", "Agriculture", "Logistics", "Travel & Tourism",
    "Financial Services", "Consulting", "Media", "Telecommunications",
    "Energy", "Mining", "Pharmaceuticals", "E-commerce",
    "Sports & Recreation", "Beauty & Wellness"
]

PAYMENT_METHODS = [
    "Credit Card", "Debit Card", "Net Banking", 
    "UPI", "Cash", "Mobile Wallet",
    "Cryptocurrency", "Bank Transfer", "RTGS",
    "NEFT", "Check", "Digital Wallet",
    "QR Code Payment", "Contactless Card",
    "Buy Now Pay Later", "EMI", "Gift Card",
    "Prepaid Card"
]

PLATFORMS = [
    "Web", "Mobile", "POS",
    "Mobile App", "Desktop App", "API Integration",
    "Social Media", "Marketplace", "Smart TV",
    "IoT Device", "Kiosk", "Voice Assistant",
    "Chat Bot", "WhatsApp", "Telegram"
]

class TransactionBase(BaseModel):
    transaction_id: str = Field(..., min_length=8, max_length=50)
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    receiver_merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    timestamp: datetime
    amount: float = Field(..., gt=0, lt=1000000)
    payment_method: str = Field(..., min_length=3, max_length=50)
    status: str = Field(..., pattern=f"^({'|'.join(TRANSACTION_STATUSES)})$")
    product_category: str
    platform: str
    customer_location: str = Field(..., min_length=2, max_length=100)
    customer_id: str = Field(..., min_length=8)
    device_id: str = Field(..., min_length=8)
    velocity_flag: bool = False
    amount_flag: bool = False
    time_flag: bool = False
    device_flag: bool = False

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

def generate_merchant_id(existing_ids=None):
    """Generate a unique merchant ID"""
    while True:
        merchant_id = f"M{random.randint(1000000, 9999999)}"
        if existing_ids is None or merchant_id not in existing_ids:
            return merchant_id

def generate_business_name() -> str:
    """Generate business name between 5 and 100 characters"""
    return fake.company()[:100]

def generate_random_date(start_year: int = 2018, end_year: int = 2024) -> datetime:
    """Generate a random registration date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    time_between_dates = end - start
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start + timedelta(days=random_number_of_days)

def generate_merchant_base(count: int) -> List[Dict]:
    """Generate base merchant profiles"""
    merchants = []
    existing_ids = set()
    
    for i in range(count):
        merchant_id = generate_merchant_id(existing_ids)
        existing_ids.add(merchant_id)
        merchant = {
            "merchant_id": merchant_id,
            "business_name": generate_business_name(),
            "business_type": random.choice(BUSINESS_TYPES),
            "registration_date": fake.date_time_between(start_date='-5y'),
            "business_model": random.choice(["Online", "Offline", "Hybrid"]),
            "product_category": random.choice(BUSINESS_TYPES),
            "average_ticket_size": round(random.uniform(100, 10000), 2),
            "gst_status": random.choice([True, False]),
            "epfo_registered": random.choice([True, False]),
            "registered_address": fake.address(),
            "city": fake.city(),
            "state": fake.state(),
            "reported_revenue": round(random.uniform(100000, 10000000), 2),
            "employee_count": random.randint(1, 1000),
            "bank_account": str(random.randint(10000000, 99999999))
        }
        merchants.append(merchant)
    return merchants

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return f"TXN{uuid.uuid4().hex[:12].upper()}"

def generate_business_hour_timestamp() -> datetime:
    """Generate timestamp within business hours"""
    current_time = datetime.now()
    days_ago = random.randint(0, 30)
    business_hour = random.randint(9, 17)
    past_date = current_time - timedelta(days=days_ago)
    return past_date.replace(
        hour=business_hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0
    )

def generate_normal_transactions(
    merchants: List[Dict], 
    days: int = 30, 
    daily_volume: Tuple[int, int] = (10, 50),
    amount_range: Tuple[float, float] = (100, 10000)
) -> List[Dict]:
    """Generate normal transaction patterns between merchants"""
    all_transactions = []
    for _ in range(days):
        # Select merchants for this day's transactions
        daily_merchants = random.sample(merchants, random.randint(5, len(merchants)))
        
        for _ in range(random.randint(*daily_volume)):
            # Select sender and receiver merchants
            sender = random.choice(daily_merchants)
            receiver = random.choice([m for m in daily_merchants if m != sender])
            
            txn = {
                "transaction_id": generate_transaction_id(),
                "merchant_id": sender["merchant_id"],
                "receiver_merchant_id": receiver["merchant_id"],
                "timestamp": generate_business_hour_timestamp(),
                "amount": round(random.uniform(*amount_range), 2),
                "payment_method": random.choice(PAYMENT_METHODS),
                "status": random.choice(TRANSACTION_STATUSES),
                "product_category": sender["product_category"],
                "platform": random.choice(PLATFORMS),
                "customer_location": sender["city"],
                "customer_id": fake.uuid4(),
                "device_id": fake.uuid4(),
                
                # Risk flags
                "velocity_flag": False,
                "amount_flag": False,
                "time_flag": False,
                "device_flag": False
            }
            all_transactions.append(txn)
    
    transaction_ids = set()
    for txn in all_transactions:
        while True:
            txn_id = generate_transaction_id()
            if txn_id not in transaction_ids:
                transaction_ids.add(txn_id)
                txn["transaction_id"] = txn_id
                break
    
    return all_transactions

def inject_fraud_pattern(
    transactions: List[Dict],
    pattern_type: str,
    config: Dict
) -> List[Dict]:
    """Inject specific fraud patterns into transactions"""
    fraudulent_transactions = transactions.copy()
    
    if pattern_type == "late_night_trading":
        # Inject late-night transactions
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["timestamp"] = txn["timestamp"].replace(
                    hour=random.randint(0, 5)
                )
                txn["time_flag"] = True
    
    elif pattern_type == "sudden_spike":
        # Create a sudden spike in transaction amounts
        spike_multiplier = config.get("multiplier", 5)
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.05):
                txn["amount"] *= spike_multiplier
                txn["amount_flag"] = True
    
    elif pattern_type == "customer_concentration":
        # Concentrate transactions from few customers
        concentrate_probability = config.get("probability", 0.2)
        few_customers = [fake.uuid4() for _ in range(3)]
        for txn in fraudulent_transactions:
            if random.random() < concentrate_probability:
                txn["customer_id"] = random.choice(few_customers)
                
    elif pattern_type == "velocity_abuse":
        # Multiple transactions in short time windows
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.15):
                txn["timestamp"] = txn["timestamp"] + timedelta(seconds=random.randint(30, 300))
                txn["velocity_flag"] = True
                
    elif pattern_type == "device_switching":
        # Rapid device switching for same customer
        device_pool = [fake.uuid4() for _ in range(3)]
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["device_id"] = random.choice(device_pool)
                txn["device_flag"] = True
                
    elif pattern_type == "location_hopping":
        # Transactions from different locations in short time
        cities = [fake.city() for _ in range(5)]
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["customer_location"] = random.choice(cities)
                
    elif pattern_type == "payment_method_cycling":
        # Cycling through different payment methods
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.15):
                txn["payment_method"] = random.choice(PAYMENT_METHODS)
                
    elif pattern_type == "round_amount":
        # Transactions with suspiciously round amounts
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["amount"] = float(round(txn["amount"], -2))  # Round to nearest 100
                txn["amount_flag"] = True

    return fraudulent_transactions

def validate_merchant_data(merchant: Dict) -> Dict:
    try:
        MerchantBase(**merchant)
        return merchant
    except ValidationError as e:
        raise ValueError(f"Invalid merchant data: {str(e)}")

def validate_transaction_data(transaction: Dict) -> Dict:
    try:
        # Ensure status is one of the allowed values
        if transaction.get('status') == 'completed':
            transaction['status'] = 'success'
            
        # Validate against the schema
        TransactionBase(**transaction)
        return transaction
    except ValidationError as e:
        raise ValueError(f"Invalid transaction data: {str(e)}")

def generate_dataset(merchant_count: int = 100, fraud_percentage: float = 0.1, fraud_patterns: List[str] = None):
    try:
        if fraud_patterns is None:
            fraud_patterns = [
                "late_night_trading", 
                "sudden_spike",
                "velocity_abuse",
                "device_switching",
                "location_hopping",
                "payment_method_cycling",
                "round_amount",
                "customer_concentration"
            ]
        if not 0 <= fraud_percentage <= 1:
            raise ValueError("fraud_percentage must be between 0 and 1")
        if merchant_count <= 0:
            raise ValueError("merchant_count must be positive")
        
        # Generate merchant base
        merchants = generate_merchant_base(merchant_count)
        
        # Generate normal transactions
        transactions = generate_normal_transactions(merchants)
        
        # Select merchants for fraud injection
        fraud_count = int(merchant_count * fraud_percentage)
        fraud_merchants = random.sample(merchants, fraud_count)
        
        # Inject fraud patterns
        for merchant in fraud_merchants:
            pattern = random.choice(fraud_patterns)
            fraud_config = {
                "probability": random.uniform(0.05, 0.2)
            }
            merchant_transactions = [
                txn for txn in transactions 
                if txn["merchant_id"] == merchant["merchant_id"]
            ]
            
            fraudulent_txns = inject_fraud_pattern(
                merchant_transactions, 
                pattern, 
                fraud_config
            )
            
            # Replace original transactions with fraudulent ones
            transactions = [
                txn for txn in transactions 
                if txn["merchant_id"] != merchant["merchant_id"]
            ] + fraudulent_txns
        
        return merchants, transactions
    except Exception as e:
        logger.error(f"Error generating dataset: {str(e)}")
        raise ValueError(f"Failed to generate dataset: {str(e)}")


# Example usage
if __name__ == "__main__":
    merchants, transactions = generate_dataset(
        merchant_count=1000, 
        fraud_percentage=0.2
    )
    
    print(f"Generated {len(merchants)} merchants")
    print(f"Generated {len(transactions)} transactions")
    print("\nSample Merchant:")
    print(merchants[0])
    print("\nSample Transaction:")
    print(transactions[0])