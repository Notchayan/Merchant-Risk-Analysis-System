from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from geopy.distance import geodesic
from collections import Counter
from .validators import validate_merchant_id, validate_transaction_timestamps
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class RiskMetricsCalculator:
    def __init__(self, transactions: List[Dict], lookback_days: int = 30):
        if not isinstance(transactions, list):
            raise ValueError("Transactions must be a list")
        
        if not validate_transaction_timestamps(transactions):
            raise ValueError("Invalid transaction timestamps")
            
        if not all(validate_merchant_id(t.get('merchant_id', '')) for t in transactions):
            raise ValueError("Invalid merchant ID format")
            
        self.transactions = transactions
        self.lookback_days = lookback_days
        self.weights = {
            'late_night_score': 0.15,
            'sudden_spike_score': 0.15,
            'velocity_abuse_score': 0.15,
            'device_switching_score': 0.10,
            'location_hopping_score': 0.10,
            'payment_cycling_score': 0.10,
            'round_amount_score': 0.10,
            'customer_concentration_score': 0.15
        }
        self._validate_weights()

    def _validate_weights(self):
        total_weight = sum(self.weights.values())
        if not 0.99 <= total_weight <= 1.01:  # Allow small float precision errors
            raise ValueError("Risk metric weights must sum to 1.0")

    def calculate_late_night_score(self) -> float:
        if not self.transactions:
            return 0
        night_txns = [
            txn for txn in self.transactions 
            if isinstance(txn['timestamp'], datetime) and  # Add type check
            (txn['timestamp'].hour >= 22 or txn['timestamp'].hour <= 5)
        ]
        return len(night_txns) / len(self.transactions)

    def calculate_sudden_spike_score(self) -> float:
        if not self.transactions:
            return 0
            
        # Group transactions by hour
        hourly_counts = Counter([txn['timestamp'].strftime("%Y-%m-%d-%H") 
                               for txn in self.transactions])
        
        # Calculate mean and std of hourly transactions
        counts = list(hourly_counts.values())
        mean = np.mean(counts)
        std = np.std(counts) if len(counts) > 1 else 0
        
        # Calculate max z-score
        max_zscore = max((max(counts) - mean) / std if std > 0 else 0, 0)
        return min(max_zscore / 3, 1)  # Normalize to [0,1]

    def calculate_velocity_abuse_score(self) -> float:
        if len(self.transactions) < 2:
            return 0.0
        
        try:
            sorted_txns = sorted(self.transactions, key=lambda x: x['timestamp'])
            intervals = []
            
            for i in range(1, len(sorted_txns)):
                try:
                    interval = (sorted_txns[i]['timestamp'] - 
                              sorted_txns[i-1]['timestamp']).total_seconds()
                    if interval > 0:
                        intervals.append(interval)
                except (TypeError, AttributeError) as e:
                    logger.error(f"Error calculating interval: {str(e)}")
                    continue
            
            if not intervals:
                return 0.0
            
            mean_interval = np.mean(intervals)
            if mean_interval == 0:
                logger.warning("Zero mean interval detected")
                return 1.0
            
            std_interval = np.std(intervals)
            cv = std_interval / mean_interval
            
            # Improved normalization using sigmoid function
            normalized_score = 1 / (1 + np.exp(-cv + 2))
            
            logger.debug(f"Velocity score components: mean={mean_interval}, std={std_interval}, cv={cv}, normalized={normalized_score}")
            return float(normalized_score)
            
        except Exception as e:
            logger.error(f"Error in velocity abuse calculation: {str(e)}", exc_info=True)
            return 0.0

    def calculate_device_switching_score(self) -> float:
        if not self.transactions:
            return 0
            
        # Count unique devices per hour
        hourly_devices = {}
        for txn in self.transactions:
            hour_key = txn['timestamp'].strftime("%Y-%m-%d-%H")
            if hour_key not in hourly_devices:
                hourly_devices[hour_key] = set()
            hourly_devices[hour_key].add(txn['device_id'])
        
        max_devices_per_hour = max(len(devices) for devices in hourly_devices.values())
        return min(max_devices_per_hour / 5, 1)  # Normalize to [0,1]

    def calculate_location_hopping_score(self) -> float:
        if not self.transactions:
            return 0
        
        # Count unique locations per hour
        hourly_locations = {}
        for txn in self.transactions:
            hour_key = txn['timestamp'].strftime("%Y-%m-%d-%H")
            if hour_key not in hourly_locations:
                hourly_locations[hour_key] = set()
            hourly_locations[hour_key].add(txn['customer_location'])
        
        max_locations_per_hour = max(len(locations) for locations in hourly_locations.values())
        return min(max_locations_per_hour / 3, 1)  # Normalize to [0,1]

    def calculate_payment_cycling_score(self) -> float:
        if not self.transactions:
            return 0
        
        # Count payment method changes per hour
        hourly_methods = {}
        for txn in self.transactions:
            hour_key = txn['timestamp'].strftime("%Y-%m-%d-%H")
            if hour_key not in hourly_methods:
                hourly_methods[hour_key] = set()
            hourly_methods[hour_key].add(txn['payment_method'])
        
        max_methods_per_hour = max(len(methods) for methods in hourly_methods.values())
        return min(max_methods_per_hour / 4, 1)  # Normalize to [0,1]

    def calculate_round_amount_score(self) -> float:
        if not self.transactions:
            return 0
        
        try:
            round_amounts = sum(1 for txn in self.transactions 
                              if isinstance(txn['amount'], (int, float)) and
                              (txn['amount'] % 100 == 0 or txn['amount'] % 1000 == 0))
            return round_amounts / len(self.transactions)
        except (KeyError, TypeError) as e:
            logger.error(f"Error calculating round amount score: {str(e)}")
            raise ValueError("Invalid amount field in transactions")

    def calculate_customer_concentration_score(self) -> float:
        if not self.transactions:
            return 0
        
        customer_counts = Counter(txn['customer_id'] for txn in self.transactions)
        values = sorted(customer_counts.values())
        n = len(values)
        if n < 2:
            return 0
        
        total_sum = np.sum(values)
        if total_sum == 0:
            return 0
        
        index = np.arange(1, n + 1)
        return min((np.sum((2 * index - n - 1) * values)) / (n * total_sum), 1)

    def calculate_composite_score(self) -> Dict[str, float]:
        try:
            scores: Dict[str, float] = {}
            
            for metric_name, weight in self.weights.items():
                try:
                    calculation_method = getattr(self, f'calculate_{metric_name}')
                    score = calculation_method()
                    
                    # Ensure score is float and within bounds
                    if not isinstance(score, (int, float)):
                        raise ValueError(f"Non-numeric score for {metric_name}: {score}")
                    
                    score = float(score)  # Convert to float
                    
                    if not 0 <= score <= 1:
                        logger.error(f"Score out of range for {metric_name}: {score}")
                        raise ValueError(f"Score must be between 0 and 1 for {metric_name}")
                    
                    scores[metric_name] = score
                    logger.debug(f"Calculated {metric_name}: {score}")
                    
                except AttributeError:
                    logger.error(f"Missing calculation method for {metric_name}")
                    raise ValueError(f"Invalid metric name: {metric_name}")
                except Exception as e:
                    logger.error(f"Error calculating {metric_name}: {str(e)}")
                    raise ValueError(f"Error in {metric_name} calculation: {str(e)}")
            
            try:
                composite_score = sum(scores[key] * self.weights[key] 
                                    for key in self.weights.keys())
                
                if not 0 <= composite_score <= 1:
                    logger.error(f"Invalid composite score: {composite_score}")
                    raise ValueError(f"Composite score out of range: {composite_score}")
                
                scores['composite_risk_score'] = composite_score
                return scores
                
            except Exception as e:
                logger.error(f"Error in final composite calculation: {str(e)}")
                raise ValueError(f"Error in composite score calculation: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}", exc_info=True)
            raise ValueError(f"Error calculating risk metrics: {str(e)}")
