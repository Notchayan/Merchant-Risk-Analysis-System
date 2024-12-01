import pytest
from datetime import datetime, timedelta
import requests
import numpy as np

BASE_URL = "https://winter-assignment.onrender.com"

def test_late_night_pattern():
    """Test detection of late-night trading pattern"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/calculate-risk-metrics/{merchant_id}")
    risk_metrics = response.json()
    
    late_night_score = risk_metrics['risk_metrics']['late_night_score']
    assert 0 <= late_night_score <= 1, "Late night score should be normalized"
    
    # Get timeline events
    events_response = requests.get(f"{BASE_URL}/merchant/{merchant_id}/timeline-events")
    events = events_response.json()['events']
    
    late_night_events = [e for e in events if e['event_type'] == 'Late-Night Transaction']
    if late_night_score > 0.5:
        assert len(late_night_events) > 0, "High late night score should have corresponding events"

def test_sudden_spike_pattern():
    """Test detection of sudden transaction volume spikes"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/calculate-risk-metrics/{merchant_id}")
    risk_metrics = response.json()
    
    spike_score = risk_metrics['risk_metrics']['sudden_spike_score']
    
    # Get transaction summary
    summary_response = requests.get(f"{BASE_URL}/generate-transaction-summary/{merchant_id}")
    summaries = summary_response.json()['summaries']
    
    if spike_score > 0.7:
        # Check for actual volume spikes in summaries
        txn_counts = [s['txn_count'] for s in summaries]
        mean_count = np.mean(txn_counts)
        max_count = max(txn_counts)
        assert max_count > mean_count * 2, "High spike score should correspond to actual volume spikes"

def test_velocity_abuse_pattern():
    """Test detection of transaction velocity abuse"""
    merchant_id = "M1234567"
    response = requests.get(f"{BASE_URL}/calculate-risk-metrics/{merchant_id}")
    risk_metrics = response.json()
    
    velocity_score = risk_metrics['risk_metrics']['velocity_abuse_score']
    
    if velocity_score > 0.6:
        # Get transactions to verify high-velocity periods
        txn_response = requests.get(f"{BASE_URL}/merchants/{merchant_id}/transactions")
        transactions = txn_response.json()
        
        # Sort transactions by timestamp
        sorted_txns = sorted(transactions, key=lambda x: datetime.fromisoformat(x['timestamp']))
        
        # Check for rapid successive transactions
        rapid_sequences = 0
        for i in range(1, len(sorted_txns)):
            time_diff = (datetime.fromisoformat(sorted_txns[i]['timestamp']) - 
                        datetime.fromisoformat(sorted_txns[i-1]['timestamp'])).total_seconds()
            if time_diff < 60:  # Less than 1 minute apart
                rapid_sequences += 1
        
        assert rapid_sequences > 0, "High velocity score should have rapid transaction sequences" 