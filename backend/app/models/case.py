from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    case_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="OPEN")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    scan = relationship("Scan", foreign_keys=[scan_id])
