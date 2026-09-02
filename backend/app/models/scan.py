from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base
from .declaration import Declaration
from .violation import Violation, ViolationStatus, ViolationSeverity

class ScanStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_A_PRODUCT = "NOT_A_PRODUCT"
    IMAGE_QUALITY_INSUFFICIENT = "IMAGE_QUALITY_INSUFFICIENT"

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String, default="Unknown Product")
    category = Column(String, default="GENERAL")
    image_path = Column(String, nullable=True)
    status = Column(SAEnum(ScanStatus, values_callable=lambda x: [e.value for e in x]), default=ScanStatus.PENDING)
    compliance_score = Column(Float, nullable=True)
    overall_status = Column(SAEnum(ViolationStatus, values_callable=lambda x: [e.value for e in x]), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    ai_debug_metrics = Column(JSON, nullable=True)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="scans")
    declarations = relationship("Declaration", back_populates="scan", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="scan", cascade="all, delete-orphan")