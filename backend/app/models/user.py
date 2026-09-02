from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    INSPECTOR = "INSPECTOR"
    ENFORCEMENT_OFFICER = "ENFORCEMENT_OFFICER"
    USER = "USER"
    MANUFACTURER = "MANUFACTURER"
    CONSUMER = "CONSUMER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.CONSUMER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    scans = relationship("Scan", foreign_keys="Scan.user_id", back_populates="user", lazy="dynamic")