import pytest
from datetime import datetime, timedelta
import requests
import json

BASE_URL = "https://winter-assignment.onrender.com"

def test_merchant_business_hours():
    """Test merchant transaction distribution across business hours"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/merchants/{merchant_id}/transactions")
    transactions = response.json()
    
    # Count transactions by hour
    hour_distribution = {}
    for txn in transactions:
        hour = datetime.fromisoformat(txn['timestamp']).hour
        hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
    
    # Business hours should have more transactions
    business_hours_count = sum(hour_distribution.get(h, 0) for h in range(9, 18))
    off_hours_count = sum(hour_distribution.get(h, 0) for h in list(range(0, 9)) + list(range(18, 24)))
    
    assert business_hours_count > off_hours_count, "Most transactions should occur during business hours"

def test_amount_distribution():
    """Test transaction amount distribution for normal patterns"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/merchants/{merchant_id}/transactions")
    transactions = response.json()
    
    amounts = [float(txn['amount']) for txn in transactions]
    
    # Calculate statistical measures
    mean_amount = sum(amounts) / len(amounts)
    sorted_amounts = sorted(amounts)
    median_amount = sorted_amounts[len(amounts)//2]
    
    # Test for reasonable amount distribution
    assert 0 < mean_amount < 10000, "Mean amount should be within reasonable range"
    assert abs(mean_amount - median_amount) < mean_amount * 0.5, "Mean and median shouldn't differ too much"

def test_customer_diversity():
    """Test customer diversity for normal merchant behavior"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/merchants/{merchant_id}/transactions")
    transactions = response.json()
    
    # Count unique customers
    unique_customers = len(set(txn['customer_id'] for txn in transactions))
    total_transactions = len(transactions)
    
    # Calculate customer concentration
    customer_ratio = unique_customers / total_transactions
    
    assert customer_ratio > 0.4, "Should have good customer diversity" 