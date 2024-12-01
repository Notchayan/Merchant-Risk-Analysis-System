from fastapi import FastAPI, Depends, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import os
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging.handlers import RotatingFileHandler
import sys
from sqlalchemy import text

# Update these imports to use relative imports
from .models import Base, Merchant, Transaction, RiskMetrics, TransactionSummary, TimelineEvent
from .schemas import MerchantBase, TransactionBase, RiskMetricsBase, TransactionSummaryBase
from .database import engine, SessionLocal, get_db, migrate_transaction_statuses
from .data_generator import generate_dataset, validate_merchant_data, validate_transaction_data
from .validators import validate_merchant_id, validate_transaction_timestamps, validate_risk_score
from .risk_metrics import RiskMetricsCalculator
from .transaction_summary import TransactionSummarizer
from .timeline_events import TimelineEventDetector
# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create log file path
log_file = os.path.join(log_dir, 'fraud_detection_api.log')

try:
    # Add file handler with proper path
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    logger.info(f"Logging initialized. Log file: {log_file}")
except Exception as e:
    logger.error(f"Failed to initialize file logging: {str(e)}")

# Add console handler for production logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(console_handler)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)


class GenerateDataRequest(BaseModel):
    merchant_count: int = Field(..., gt=0, lt=10000)
    fraud_percentage: float = Field(..., ge=0, le=1)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Fraud Detection API")
    try:
        # Test database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
            # Run migrations
            migrate_transaction_statuses(db)
            logger.info("Transaction status migration completed")
            
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Fraud Detection API")


@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    """
    return {
        "name": "Merchant Risk Analysis System",
        "version": "1.0.0",
        "description": "API for analyzing merchant transactions, calculating risk metrics, and detecting unusual events",
        "endpoints": {
            "risk_metrics": {
                "calculate": "/calculate-risk-metrics/{merchant_id}",
                "get_latest": "/merchant/{merchant_id}/risk-metrics/latest",
                "get_history": "/merchant/{merchant_id}/risk-metrics/history"
            },
            "transaction_summaries": {
                "generate": "/generate-transaction-summary/{merchant_id}",
                "get": "/merchant/{merchant_id}/transaction-summaries"
            },
            "timeline_events": {
                "generate": "/merchant/{merchant_id}/timeline-events",
                "get": "/merchant/{merchant_id}/timeline-events"
            },
            "data_retrieval": {
                "get_merchants": "/merchants/",
                "get_transactions": "/transactions/",
                "get_merchant_transactions": "/merchant/{merchant_id}/transactions"
            }
        },
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "contact": {
            "name": "chayan",
            "github": "https://github.com/Notchayan"
        }
    }
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "version": "1.0.0"
    }


@app.post("/generate-and-store-data/")
async def generate_and_store_data(
    request: GenerateDataRequest,
    db: Session = Depends(get_db)
):
    try:
        merchants, transactions = generate_dataset(
            merchant_count=request.merchant_count,
            fraud_percentage=request.fraud_percentage
        )
        
        # Validate all data before storing
        validated_merchants = [validate_merchant_data(m) for m in merchants]
        validated_transactions = [validate_transaction_data(t) for t in transactions]
        
        # Store in database within transaction
        try:
            for merchant_data in validated_merchants:
                db_merchant = Merchant(**merchant_data)
                db.add(db_merchant)
            
            for transaction_data in validated_transactions:
                db_transaction = Transaction(**transaction_data)
                db.add(db_transaction)
            
            db.commit()
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
        return {
            "message": "Data generated and stored successfully",
            "merchant_count": len(merchants),
            "transaction_count": len(transactions)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/merchants/")
async def read_merchants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, gt=0, le=1000),
    db: Session = Depends(get_db)
):
    try:
        merchants = db.query(Merchant).offset(skip).limit(limit).all()
        return merchants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/", response_model=List[TransactionBase])
async def read_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching transactions with skip={skip}, limit={limit}")
    try:
        transactions = db.query(Transaction).offset(skip).limit(limit).all()
        logger.info(f"Successfully retrieved {len(transactions)} transactions")
        return transactions
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching transactions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/merchant/{merchant_id}", response_model=MerchantBase)
async def get_merchant_by_id(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    try:
        merchant = db.query(Merchant)\
            .filter(Merchant.merchant_id == merchant_id)\
            .first()
        
        if not merchant:
            raise HTTPException(
                status_code=404,
                detail=f"Merchant with ID {merchant_id} not found"
            )
        
        return merchant
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/merchant/{merchant_id}/transactions", response_model=List[TransactionBase])
async def get_merchant_transactions(
    merchant_id: str = Path(..., pattern="^M[0-9]{7}$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=100, gt=0, le=1000),
    skip: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    logger.info(
        f"Fetching transactions for merchant {merchant_id} "
        f"(start_date={start_date}, end_date={end_date}, "
        f"limit={limit}, skip={skip})"
    )
    try:
        query = db.query(Transaction)\
            .filter(Transaction.merchant_id == merchant_id)
        
        if start_date:
            query = query.filter(Transaction.timestamp >= start_date)
        if end_date:
            query = query.filter(Transaction.timestamp <= end_date)
            
        transactions = query\
            .order_by(Transaction.timestamp.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        if not transactions:
            logger.warning(f"No transactions found for merchant {merchant_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No transactions found for merchant {merchant_id}"
            )
            
        logger.info(f"Successfully retrieved {len(transactions)} transactions for merchant {merchant_id}")
        return transactions
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching transactions for merchant {merchant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching transactions for merchant {merchant_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transaction/{transaction_id}", response_model=TransactionBase)
async def get_transaction_by_id(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    try:
        transaction = db.query(Transaction)\
            .filter(Transaction.transaction_id == transaction_id)\
            .first()
            
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )
            
        return transaction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-risk-metrics/{merchant_id}")
async def calculate_risk_metrics(
    merchant_id: str,
    lookback_days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    if not validate_merchant_id(merchant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid merchant ID format"
        )
    
    try:
        # Get merchant transactions with validation
        transactions = db.query(Transaction)\
            .filter(
                Transaction.merchant_id == merchant_id,
                Transaction.timestamp >= datetime.now() - timedelta(days=lookback_days)
            )\
            .all()
        
        if not transactions:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for this merchant"
            )
        
        # Convert transactions to dictionary safely
        transaction_dicts = [
            {
                'transaction_id': t.transaction_id,
                'merchant_id': t.merchant_id,
                'timestamp': t.timestamp,
                'amount': t.amount,
                'payment_method': t.payment_method,
                'status': t.status,
                'customer_id': t.customer_id,
                'device_id': t.device_id,
                'customer_location': t.customer_location
            }
            for t in transactions
        ]
        
        try:
            # Calculate risk metrics with validation
            calculator = RiskMetricsCalculator(
                transaction_dicts,
                lookback_days=lookback_days
            )
            
            metrics = calculator.calculate_composite_score()
            
            # Add timestamp to metrics
            current_time = datetime.now()
            
            # Store risk metrics
            risk_metrics = RiskMetrics(
                merchant_id=merchant_id,
                timestamp=current_time,
                **metrics
            )
            
            db.add(risk_metrics)
            db.commit()
            
            return {
                "merchant_id": merchant_id,
                "risk_metrics": metrics,
                "calculation_timestamp": current_time
            }
            
        except ValueError as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in calculate_risk_metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in calculate_risk_metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while calculating risk metrics"
        )

@app.get("/merchant/{merchant_id}/risk-metrics/latest")
async def get_latest_risk_metrics(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    metrics = db.query(RiskMetrics)\
        .filter(RiskMetrics.merchant_id == merchant_id)\
        .order_by(RiskMetrics.timestamp.desc())\
        .first()
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="No risk metrics found for this merchant"
        )
    #thanks
    return {
        "merchant_id": merchant_id,
        "timestamp": metrics.timestamp,
        "metrics": {
            "late_night_score": metrics.late_night_score,
            "sudden_spike_score": metrics.sudden_spike_score,
            "velocity_abuse_score": metrics.velocity_abuse_score,
            "device_switching_score": metrics.device_switching_score,
            "location_hopping_score": metrics.location_hopping_score,
            "payment_cycling_score": metrics.payment_cycling_score,
            "round_amount_score": metrics.round_amount_score,
            "customer_concentration_score": metrics.customer_concentration_score,
            "composite_risk_score": metrics.composite_risk_score
        }
    }

@app.get("/merchant/{merchant_id}/risk-metrics/history")
async def get_risk_metrics_history(
    merchant_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    metrics = db.query(RiskMetrics)\
        .filter(
            RiskMetrics.merchant_id == merchant_id,
            RiskMetrics.timestamp >= datetime.now() - timedelta(days=days)
        )\
        .order_by(RiskMetrics.timestamp.desc())\
        .all()
    
    return {
        "merchant_id": merchant_id,
        "history": [
            {
                "timestamp": m.timestamp,
                "metrics": {
                    "late_night_score": m.late_night_score,
                    "sudden_spike_score": m.sudden_spike_score,
                    "velocity_abuse_score": m.velocity_abuse_score,
                    "device_switching_score": m.device_switching_score,
                    "location_hopping_score": m.location_hopping_score,
                    "payment_cycling_score": m.payment_cycling_score,
                    "round_amount_score": m.round_amount_score,
                    "customer_concentration_score": m.customer_concentration_score,
                    "composite_risk_score": m.composite_risk_score
                }
            }
            for m in metrics
        ]
    }


@app.post("/generate-transaction-summary/{merchant_id}")
async def generate_transaction_summary(
    merchant_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    try:
        if not validate_merchant_id(merchant_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid merchant ID format"
            )
            
        summarizer = TransactionSummarizer(db)
        summaries = []
        
        current_date = start_date
        while current_date <= end_date:
            summary = summarizer.generate_daily_summary(merchant_id, current_date)
            if summary:
                stored_summary = summarizer.store_summary(summary)
                summaries.append(stored_summary)
            current_date += timedelta(days=1)
            
        return {
            "merchant_id": merchant_id,
            "summary_count": len(summaries),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "summaries": summaries
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating transaction summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error generating transaction summary")

@app.get("/merchant/{merchant_id}/transaction-summaries")
async def get_transaction_summaries(
    merchant_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(TransactionSummary)\
            .filter(TransactionSummary.merchant_id == merchant_id)
            
        if start_date:
            query = query.filter(TransactionSummary.date >= start_date)
        if end_date:
            query = query.filter(TransactionSummary.date <= end_date)
            
        summaries = query.order_by(TransactionSummary.date.desc()).all()
        
        if not summaries:
            raise HTTPException(
                status_code=404,
                detail="No transaction summaries found for this merchant"
            )
            
        return {
            "merchant_id": merchant_id,
            "summaries": summaries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction summaries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching transaction summaries")

@app.post("/merchant/{merchant_id}/timeline-events")
async def generate_timeline_events(
    merchant_id: str,
    start_date: datetime = Query(..., description="Start date for event detection"),
    end_date: datetime = Query(..., description="End date for event detection"),
    event_types: List[str] = Query(default=None, description="Filter by event types"),
    db: Session = Depends(get_db)
):
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
        
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 90 days"
        )
        
    try:
        # Get transactions for the period
        transactions = db.query(Transaction)\
            .filter(
                Transaction.merchant_id == merchant_id,
                Transaction.timestamp >= start_date,
                Transaction.timestamp <= end_date
            )\
            .all()
        
        if not transactions:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for this period"
            )
        
        # Convert to dictionary format
        transaction_dicts = [
            {
                'transaction_id': t.transaction_id,
                'merchant_id': t.merchant_id,
                'timestamp': t.timestamp,
                'amount': t.amount,
                'payment_method': t.payment_method,
                'status': t.status,
                'customer_id': t.customer_id,
                'device_id': t.device_id,
                'customer_location': t.customer_location
            }
            for t in transactions
        ]
        
        # Detect events
        detector = TimelineEventDetector(db)
        events = detector.detect_events(transaction_dicts)
        
        # Store events in database
        stored_events = []
        for event in events:
            db_event = TimelineEvent(**event)
            db.add(db_event)
            stored_events.append(event)
        
        db.commit()
        
        return {
            "merchant_id": merchant_id,
            "event_count": len(stored_events),
            "events": stored_events
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating timeline events: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating timeline events: {str(e)}"
        )

@app.get("/merchant/{merchant_id}/timeline-events")
async def get_timeline_events(
    merchant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(TimelineEvent)\
            .filter(TimelineEvent.merchant_id == merchant_id)
        
        if start_date:
            query = query.filter(TimelineEvent.timestamp >= start_date)
        if end_date:
            query = query.filter(TimelineEvent.timestamp <= end_date)
        if event_type:
            query = query.filter(TimelineEvent.event_type == event_type)
        if severity:
            query = query.filter(TimelineEvent.severity == severity)
            
        events = query.order_by(TimelineEvent.timestamp.desc()).all()
        
        return {
            "merchant_id": merchant_id,
            "events": events
        }
        
    except Exception as e:
        logger.error(f"Error fetching timeline events: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching timeline events: {str(e)}"
        )

