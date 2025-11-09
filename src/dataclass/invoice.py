from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Modelo Pydantic para os produtos, já que eles também podem
# ser editados e enviados na requisição de PATCH.
class ProductPatch(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None

class InvoicePatchRequest(BaseModel):
    invoice_number: Optional[str] = None
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    total_amount: Optional[float] = None
    issue_date: Optional[date] = None 
    
    due_date: Optional[date] = None
    supplier_cnpj: Optional[str] = None
    customer_cnpj: Optional[str] = None
    discount_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    access_key: Optional[str] = None
    fiscal_protocol: Optional[str] = None
    
    products: Optional[List[ProductPatch]] = None