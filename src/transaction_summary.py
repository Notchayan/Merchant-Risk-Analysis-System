from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from .models import Transaction, TransactionSummary
import logging

logger = logging.getLogger(__name__)

class TransactionSummarizer:
    def __init__(self, db: Session):
        self.db = db

    def generate_daily_summary(self, merchant_id: str, date: datetime) -> Dict:
        try:
            # Get transactions for the specified day
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            transactions = self.db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.timestamp >= start_date,
                Transaction.timestamp < end_date
            ).all()
            
            if not transactions:
                return None
            
            # Convert to pandas DataFrame for easier aggregation
            df = pd.DataFrame([{
                'amount': t.amount,
                'customer_id': t.customer_id,
                'payment_method': t.payment_method
            } for t in transactions])
            
            summary = {
                'merchant_id': merchant_id,
                'date': start_date,
                'txn_count': len(transactions),
                'total_volume': float(df['amount'].sum()),
                'avg_amount': float(df['amount'].mean()),
                'max_amount': float(df['amount'].max()),
                'min_amount': float(df['amount'].min()),
                'unique_customers': len(df['customer_id'].unique()),
                'unique_payment_methods': len(df['payment_method'].unique())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for merchant {merchant_id}: {str(e)}")
            raise

    def store_summary(self, summary: Dict) -> TransactionSummary:
        try:
            db_summary = TransactionSummary(**summary)
            self.db.add(db_summary)
            self.db.commit()
            self.db.refresh(db_summary)
            return db_summary
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing summary: {str(e)}")
            raise 