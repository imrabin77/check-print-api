from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Check(Base):
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    check_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, default="GENERATED")  # GENERATED | PRINTED | VOID
    issue_date = Column(Date, nullable=False)
    memo = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor = relationship("Vendor")
    invoice = relationship("Invoice", back_populates="check", foreign_keys="Invoice.check_id", uselist=False)
