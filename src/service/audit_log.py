from fastapi import Request
from datetime import datetime, timezone
from src.config.firestore import firestore_db

def create_audit_log(
    request: Request,
    action: str,
    status: str,
    invoice_id: str = None,
    details: dict = None
):
    """
    Cria um documento de log na coleção 'audit_logs' do Firestore.
    """
    try:
        log_entry = {
            "requestId": str(request.state.request_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "status": status,
            "invoiceId": invoice_id,
            "details": details or {},
            "actor": {
                "userId": getattr(request.state, "user_id", "system"), 
                "ipAddress": request.client.host
            }
        }

        firestore_db.collection('audit_logs').add(log_entry)

    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao gravar log de auditoria: {e}")