from fastapi import Body
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from src.service.invoice import read_and_save_invoice, update_invoice_fields
from src.model.invoice import Invoice
from src.dataclass.invoice import InvoicePatchRequest


invoice_router = APIRouter(prefix="/invoiceAgent", tags=["Invoice Agent"])
@invoice_router.post("/readInvoice")
async def read_invoice(pdf_file: bytes = Body('', media_type="application/pdf")):
    invoice: Invoice = await read_and_save_invoice(pdf_file)

    return JSONResponse(invoice.model_dump(), status_code=200)

@invoice_router.patch("/updateInvoiceFields/{invoice_id}")
async def partial_update_invoice(invoice_id: int, invoice_update_data: InvoicePatchRequest):
    update_data: Invoice = update_invoice_fields(invoice_id, invoice_update_data)

    return JSONResponse(update_data, status_code=200)