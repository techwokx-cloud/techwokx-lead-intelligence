from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create database directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///data/company_research.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResearchHistory(Base):
    __tablename__ = "research_history"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    website = Column(String)
    searched_at = Column(DateTime)
    result_summary = Column(String)

class CRMCompany(Base):
    __tablename__ = "crm_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    domain = Column(String, unique=True, index=True)
    website = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    lead_score = Column(Integer)
    lead_status = Column(String)
    created_at = Column(DateTime)
    last_research = Column(DateTime)
    research_data = Column(Text)  # JSON data

class CRMActivity(Base):
    __tablename__ = "crm_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    activity_type = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    user_id = Column(Integer, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_session():
    """Get database session"""
    return SessionLocal()
