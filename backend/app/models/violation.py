from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)

    rule_id = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    severity = Column(String(50), default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)

    scan = relationship("Scan", back_populates="violations")
