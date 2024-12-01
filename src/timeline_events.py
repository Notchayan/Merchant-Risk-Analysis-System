from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TimelineEventDetector:
    def __init__(self, db: Session):
        self.db = db
        
    def detect_events(self, transactions: List[Dict]) -> List[Dict]:
        events = []
        events.extend(self.detect_round_amounts(transactions))
        events.extend(self.detect_late_night_transactions(transactions))
        events.extend(self.detect_sudden_spikes(transactions))
        return events
    
    def detect_round_amounts(self, transactions: List[Dict]) -> List[Dict]:
        events = []
        for txn in transactions:
            try:
                amount = float(txn['amount'])
                if amount % 100 == 0 or amount % 1000 == 0:
                    events.append({
                        'event_type': 'Round Amount Transaction',
                        'timestamp': txn['timestamp'],
                        'merchant_id': txn['merchant_id'],
                        'details': {
                            'amount': amount,
                            'transaction_id': txn['transaction_id'],
                            'payment_method': txn['payment_method']
                        },
                        'severity': 'LOW'
                    })
            except (KeyError, ValueError, TypeError) as e:
                logger.error(f"Error processing transaction {txn.get('transaction_id', 'unknown')}: {str(e)}")
                continue
        return events
    
    def detect_late_night_transactions(self, transactions: List[Dict]) -> List[Dict]:
        events = []
        for txn in transactions:
            hour = txn['timestamp'].hour
            if hour >= 22 or hour <= 5:
                events.append({
                    'event_type': 'Late-Night Transaction',
                    'timestamp': txn['timestamp'],
                    'merchant_id': txn['merchant_id'],
                    'details': {
                        'amount': txn['amount'],
                        'transaction_id': txn['transaction_id'],
                        'hour': hour
                    },
                    'severity': 'MEDIUM'
                })
        return events
    
    def detect_sudden_spikes(self, transactions: List[Dict]) -> List[Dict]:
        if len(transactions) < 10:
            return []
        
        events = []
        try:
            hourly_counts = Counter([
                txn['timestamp'].strftime("%Y-%m-%d-%H") 
                for txn in sorted(transactions, key=lambda x: x['timestamp'])
            ])
            
            counts = list(hourly_counts.values())
            if not counts:
                return events
            
            mean = np.mean(counts)
            std = np.std(counts) if len(counts) > 1 else 0
            
            if std == 0:
                return events
            
            for hour, count in hourly_counts.items():
                z_score = (count - mean) / std
                if z_score > 2.5:
                    events.append({
                        'event_type': 'Sudden Transaction Spike',
                        'timestamp': datetime.strptime(hour, "%Y-%m-%d-%H"),
                        'merchant_id': transactions[0]['merchant_id'],
                        'details': {
                            'transaction_count': count,
                            'normal_average': round(mean, 2),
                            'z_score': round(z_score, 2),
                            'hourly_threshold': round(mean + 2.5 * std, 2)
                        },
                        'severity': 'HIGH' if z_score > 3 else 'MEDIUM'
                    })
        except Exception as e:
            logger.error(f"Error in sudden spike detection: {str(e)}")
        return events 