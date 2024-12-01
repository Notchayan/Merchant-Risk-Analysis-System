from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import text

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# Handle Render's Postgres connection string format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        logger.debug("Database connection established")
        yield db
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        logger.debug("Closing database connection")
        db.close()

def migrate_transaction_statuses(db: Session):
    """Migrate transaction statuses from 'completed' to 'success'"""
    try:
        db.execute(
            text("""
            UPDATE transactions 
            SET status = 'success' 
            WHERE status = 'completed'
            """)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to migrate transaction statuses: {str(e)}")
        raise