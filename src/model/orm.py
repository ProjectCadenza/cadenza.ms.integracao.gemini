from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class ProductDB(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255))
    quantity = Column(Float)
    unit_price = Column(Float)
    total_amount = Column(Float)
    
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    invoice = relationship("InvoiceDB", back_populates="products")

class InvoiceDB(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50))
    due_date = Column(String(10))
    issue_date = Column(String(10))
    supplier_cnpj = Column(String(100))
    supplier_name = Column(String(255))
    customer_cnpj = Column(String(20))
    customer_name = Column(String(255))
    total_amount = Column(Float)
    discount_amount = Column(Float)
    tax_amount = Column(Float)
    access_key = Column(String(50))
    fiscal_protocol = Column(String(50))
    raw_file_uri = Column(String(2083))
    json_file_uri = Column(String(2083))
    created_at = Column(DateTime, default=datetime.now())

    products = relationship("ProductDB", back_populates="invoice", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="invoice", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), index=True, nullable=False)
    action = Column(String(20)) 
    request_path = Column(String(50))
    created_at = Column(DateTime, default=datetime.now())
    service_name = Column(String(50), index=True, nullable=False, default="ms-integracao-gemini")

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice = relationship("InvoiceDB", back_populates="audit_logs")