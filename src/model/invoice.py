from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
import re

null_values = ["null", "n/a", "none", ""]

class Product(BaseModel):
    description: Optional[str] = Field(None, description="Product or service description")
    quantity: Optional[float] = Field(None, description="Quantity of the item")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total_amount: Optional[float] = Field(None, description="Total amount for this line item")
    
    @field_validator('*', mode='before')
    def null_to_none(cls, value: Any):
        if isinstance(value, str) and value.lower() in null_values:
            return None
        return value

class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    due_date: Optional[str] = Field(None, description="Due date of the invoice (YYYY-MM-DD)")
    issue_date: Optional[str] = Field(None, description="Date the invoice was issued (YYYY-MM-DD)")
    
    supplier_cnpj: Optional[str] = Field(None, description="CNPJ of the service provider")
    supplier_name: Optional[str] = Field(None, description="Name of the service provider")
    customer_cnpj: Optional[str] = Field(None, description="CNPJ or CPF of the service recipient")
    customer_name: Optional[str] = Field(None, description="Name of the service recipient")
    
    total_amount: Optional[float] = Field(None, description="Total amount of the invoice")
    discount_amount: Optional[float] = Field(None, description="Total discount applied")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    
    products: Optional[List[Product]] = Field(None, description="List of products or services")
    
    access_key: Optional[str] = Field(None, description="Access key of the electronic invoice")
    fiscal_protocol: Optional[str] = Field(None, description="Protocol number of the fiscal authority")
    
    @field_validator('supplier_cnpj', 'customer_cnpj', mode='before')
    def remove_non_numeric_chars(cls, value: Any):
        if isinstance(value, str):
            return re.sub(r'\D', '', value).zfill(14)
        return value

    @field_validator('*', mode='before')
    def null_to_none(cls, value: Any):
        if isinstance(value, str) and value.lower() in null_values:
            return None
        return value