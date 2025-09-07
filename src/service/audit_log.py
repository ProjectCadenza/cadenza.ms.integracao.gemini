from sqlalchemy.orm import Session
from src.model.orm import AuditLog, InvoiceDB
from fastapi import Request

def log_audit(db: Session, request: Request, invoice: InvoiceDB):
    try:
        audit = AuditLog(
            request_id=request.state.request_id,
            action=request.method,
            invoice_id=invoice.id,
            request_path=request.url.path
        )
        db.add(audit)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()