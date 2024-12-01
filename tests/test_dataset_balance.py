import pytest
import requests
import numpy as np
from collections import Counter

BASE_URL = "https://winter-assignment.onrender.com"

def test_fraud_normal_ratio():
    """Test the balance between fraudulent and normal merchants"""
    response = requests.get(f"{BASE_URL}/merchants")
    merchants = response.json()
    
    # Get risk metrics for all merchants
    high_risk_count = 0
    total_merchants = len(merchants)
    
    for merchant in merchants:
        risk_response = requests.get(f"{BASE_URL}/calculate-risk-metrics/{merchant['merchant_id']}")
        risk_metrics = risk_response.json()
        if risk_metrics['risk_metrics']['composite_risk_score'] > 0.7:
            high_risk_count += 1
    
    fraud_ratio = high_risk_count / total_merchants
    assert 0.05 <= fraud_ratio <= 0.3, "Fraud ratio should be realistic (5-30%)"

def test_pattern_distribution():
    """Test the distribution of different fraud patterns"""
    response = requests.get(f"{BASE_URL}/merchants")
    merchants = response.json()
    
    pattern_counts = Counter()
    
    for merchant in merchants[:100]:  # Test first 100 merchants
        events_response = requests.get(f"{BASE_URL}/merchant/{merchant['merchant_id']}/timeline-events")
        events = events_response.json().get('events', [])
        
        for event in events:
            pattern_counts[event['event_type']] += 1
    
    # Check pattern diversity
    pattern_types = len(pattern_counts)
    assert pattern_types >= 5, "Should have at least 5 different fraud patterns"
    
    # Check pattern balance
    pattern_frequencies = np.array(list(pattern_counts.values()))
    variation_coefficient = np.std(pattern_frequencies) / np.mean(pattern_frequencies)
    assert variation_coefficient < 0.5, "Patterns should be relatively balanced"

def test_overall_statistics():
    """Test overall dataset statistics"""
    response = requests.get(f"{BASE_URL}/merchants")
    merchants = response.json()
    
    # Test business type distribution
    business_types = Counter(m['business_type'] for m in merchants)
    assert len(business_types) >= 10, "Should have diverse business types"
    
    # Test transaction volume distribution
    volumes = []
    for merchant in merchants[:50]:  # Test first 50 merchants
        summary_response = requests.get(f"{BASE_URL}/generate-transaction-summary/{merchant['merchant_id']}")
        summaries = summary_response.json().get('summaries', [])
        if summaries:
            volumes.append(sum(s['total_volume'] for s in summaries))
    
    # Calculate volume statistics
    volume_mean = np.mean(volumes)
    volume_std = np.std(volumes)
    volume_cv = volume_std / volume_mean
    
    assert volume_cv < 1.0, "Transaction volumes should show reasonable variation" 