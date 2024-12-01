from datetime import datetime
from typing import Dict, List
import re
from pydantic import ValidationError

def validate_merchant_id(merchant_id: str) -> bool:
    return bool(re.match(r"^M[0-9]{7}$", merchant_id))

def validate_transaction_timestamps(transactions: List[Dict]) -> bool:
    return all(
        isinstance(t.get('timestamp'), datetime)
        for t in transactions
    )

def validate_amount(amount: float) -> bool:
    return isinstance(amount, (int, float)) and 0 < amount < 1000000

def validate_risk_score(score: float) -> bool:
    return isinstance(score, float) and 0 <= score <= 1

def validate_business_model(model: str) -> bool:
    return model in ["Online", "Offline", "Hybrid"]
