from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from enum import Enum

Base = declarative_base()

class LeadStatus(str, Enum):
    FOUND = "Found"
    ENRICHED = "Enriched"
    MISSING_INFO = "Missing_Info"
    CONTACTED = "Contacted"
    FOLLOWUP_1 = "Followup_1"
    FOLLOWUP_2 = "Followup_2"
    FOLLOWUP_3 = "Followup_3"
    REPLIED = "Replied"
    CLOSED = "Closed"

class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    clinic_name = Column(String)
    website = Column(String, unique=True)
    email = Column(String)
    phone = Column(String)
    status = Column(String, default=LeadStatus.FOUND)
    last_contacted = Column(DateTime, nullable=True)
    follow_up_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

engine = create_engine('sqlite:///data/leads.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()
