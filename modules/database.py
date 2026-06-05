from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()
DB_PATH = os.getenv("DB_PATH", "data/leads.db")
os.makedirs("data", exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    website = Column(String(500))
    industry = Column(String(100))
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    description = Column(Text)
    confidence_score = Column(Float, default=0)
    lead_score = Column(Float, default=0)
    lead_status = Column(String(20), default="Cold")  # Hot/Warm/Cold
    crm_stage = Column(String(50), default="New")
    dns_score = Column(Integer, default=0)
    ssl_valid = Column(Boolean, default=False)
    website_up = Column(Boolean, default=False)
    has_spf = Column(Boolean, default=False)
    has_dmarc = Column(Boolean, default=False)
    has_mx = Column(Boolean, default=False)
    email_provider = Column(String(100))
    tech_stack = Column(Text)
    ai_summary = Column(Text)
    notes = Column(Text)
    follow_up_date = Column(DateTime)
    proposal_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="company", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    role = Column(String(100))
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="contacts")


class ResearchHistory(Base):
    __tablename__ = "research_history"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255))
    website = Column(String(500))
    searched_at = Column(DateTime, default=datetime.utcnow)
    result_summary = Column(Text)


class CompanyCandidate(Base):
    __tablename__ = "company_candidates"
    id = Column(Integer, primary_key=True)
    search_term = Column(String(255))
    candidate_name = Column(String(255))
    candidate_website = Column(String(500))
    confidence_score = Column(Float, default=0)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    activity_type = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="activities")


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return Session()


init_db()
