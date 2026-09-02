from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Declaration(Base):
    __tablename__ = "declarations"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)

    mrp = Column(String(100), nullable=True)
    net_quantity = Column(String(100), nullable=True)
    mfd_date = Column(String(100), nullable=True)
    expiry_date = Column(String(100), nullable=True)
    country_of_origin = Column(String(100), nullable=True)
    customer_care = Column(String(200), nullable=True)
    manufacturer_details = Column(String(300), nullable=True)

    scan = relationship("Scan", back_populates="declarations")
