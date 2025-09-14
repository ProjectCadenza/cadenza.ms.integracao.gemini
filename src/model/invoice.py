from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
import re

null_values = ["null", "n/a", "none", ""]

class Product(BaseModel):
    id: Optional[int] = Field(None, description="ID sequencial e incremental do produto dentro da nota fiscal")
    
    description: Optional[str] = Field(None, description="Descrição do produto ou serviço")
    quantity: Optional[float] = Field(None, description="Quantidade do item")
    unit_price: Optional[float] = Field(None, description="Preço por unidade")
    total_amount: Optional[float] = Field(None, description="Valor total para este item da linha")
    
    @field_validator('*', mode='before')
    def null_to_none(cls, value: Any):
        if isinstance(value, str) and value.lower() in null_values:
            return None
        return value

class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(None, description="Número da nota fiscal")
    due_date: Optional[str] = Field(None, description="Data de vencimento da nota (YYYY-MM-DD)")
    issue_date: Optional[str] = Field(None, description="Data de emissão da nota (YYYY-MM-DD)")
    
    supplier_cnpj: Optional[str] = Field(None, description="CNPJ do fornecedor do serviço")
    supplier_name: Optional[str] = Field(None, description="Nome do fornecedor do serviço")
    customer_cnpj: Optional[str] = Field(None, description="CNPJ ou CPF do cliente")
    customer_name: Optional[str] = Field(None, description="Nome do cliente")
    
    total_amount: Optional[float] = Field(None, description="Valor total da nota fiscal")
    discount_amount: Optional[float] = Field(None, description="Desconto total aplicado")
    tax_amount: Optional[float] = Field(None, description="Valor total de impostos")
    
    products: Optional[List[Product]] = Field(None, description="Lista de produtos ou serviços")
    
    access_key: Optional[str] = Field(None, description="Chave de acesso da nota fiscal eletrônica")
    fiscal_protocol: Optional[str] = Field(None, description="Número de protocolo da autoridade fiscal")
    
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