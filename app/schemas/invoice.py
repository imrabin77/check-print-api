from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    store_number: Optional[str] = None
    vendor_id: int
    vendor_name: Optional[str] = None
    amount: Decimal
    invoice_date: date
    status: str
    check_id: Optional[int] = None
    check_number: Optional[str] = None
    notes: Optional[str] = None
    attachment_filename: Optional[str] = None
    source_type: Optional[str] = None
    imported_by_name: Optional[str] = None
    imported_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    invoice_number: str
    store_number: str
    vendor_name: str
    amount: Decimal
    invoice_date: date
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class ImportSummary(BaseModel):
    total_rows: int
    imported: int
    skipped_duplicates: int
    errors: list[str]
