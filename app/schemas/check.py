from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class CheckResponse(BaseModel):
    id: int
    check_number: str
    vendor_id: int
    vendor_name: Optional[str] = None
    amount: Decimal
    status: str
    issue_date: date
    memo: Optional[str] = None
    invoice_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateCheckRequest(BaseModel):
    invoice_id: int
    memo: Optional[str] = None
