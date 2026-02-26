from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    store_number = Column(String(50), nullable=True, index=True)  # which store/location this invoice is from
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    invoice_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="PENDING")
    # PENDING -> APPROVED -> CHECK_GENERATED -> PRINTED -> VOID
    check_id = Column(Integer, ForeignKey("checks.id"), nullable=True)
    notes = Column(String(1000))
    attachment_filename = Column(String(500), nullable=True)  # stored filename for uploaded PDF/image
    source_type = Column(String(20), nullable=True, default="csv")  # csv, excel, manual, upload
    imported_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="invoices")
    check = relationship("Check", back_populates="invoice", foreign_keys=[check_id])
    imported_by = relationship("User", foreign_keys=[imported_by_id])
