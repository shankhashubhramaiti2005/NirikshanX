from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    image_filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    is_valid = Column(Boolean, default=False)
    status = Column(String(50), default="PROCESSED") # PASSED, REJECTED, NON_COMPLIANT
    processing_time_seconds = Column(Float, default=0.0)

    quality_metrics = Column(JSON, nullable=True)
    product_metrics = Column(JSON, nullable=True)
    ocr_metrics = Column(JSON, nullable=True)
    compliance_result = Column(JSON, nullable=True)
    ai_debug_metrics = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    declarations = relationship("Declaration", back_populates="scan", uselist=False)
    violations = relationship("Violation", back_populates="scan", cascade="all, delete-orphan")
    legal_case = relationship("LegalCase", back_populates="scan", uselist=False)
