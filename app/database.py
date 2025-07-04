from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_jobs.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(200), nullable=False, index=True)
    location = Column(String(200), nullable=True, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String(10), default="DKK")
    job_type = Column(String(50), nullable=True, index=True)  # full-time, part-time, contract, freelance
    remote_ok = Column(Boolean, default=False)
    url = Column(String(500), nullable=False, unique=True)
    source = Column(String(100), nullable=False, index=True)  # linkedin, jobnet, glassdoor, etc.
    posted_date = Column(DateTime, nullable=True)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # AI-specific fields
    ai_keywords = Column(Text, nullable=True)  # JSON string of matched keywords
    relevance_score = Column(Float, default=0.0)  # AI relevance score 0-1
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', location='{self.location}')>"

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database dependency for FastAPI
def get_db_session() -> Session:
    """Get database session for direct use"""
    return SessionLocal()