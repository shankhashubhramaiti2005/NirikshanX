from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class ViolationSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ViolationStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_A_PRODUCT = "NOT_A_PRODUCT"
    IMAGE_QUALITY_INSUFFICIENT = "IMAGE_QUALITY_INSUFFICIENT"

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    rule_id = Column(String, nullable=False)
    field = Column(String, nullable=False)
    status = Column(SAEnum(ViolationStatus), nullable=False)
    severity = Column(SAEnum(ViolationSeverity), nullable=False)
    message = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    confidence = Column(Float, default=1.0)
    
    scan = relationship("Scan", back_populates="violations")
