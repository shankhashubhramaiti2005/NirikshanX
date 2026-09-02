from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from ..database import Base

class Declaration(Base):
    __tablename__ = "declarations"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    field_name = Column(String, nullable=False)
    extracted_value = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    bounding_box = Column(JSON, nullable=True)
    is_present = Column(Boolean, default=False)
    
    scan = relationship("Scan", back_populates="declarations")
