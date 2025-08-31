from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel
from datetime import date

@dataclass
class InvoicePatchRequest(BaseModel):
    invoice_number: Optional[str] = None
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    total_amount: Optional[float] = None
    issue_date: Optional[date] = None