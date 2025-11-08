from fastapi import Request, UploadFile, File, Depends
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from src.service.invoice import read_and_save_invoice_firestore, update_invoice_fields_firestore
from src.model.invoice import Invoice
from src.dataclass.invoice import InvoicePatchRequest
from src.utils.colored_logger import log

invoice_router = APIRouter(prefix="/invoiceAgent", tags=["Invoice Agent"])

@invoice_router.post("/readInvoice")
async def read_invoice(request: Request, pdf_file: UploadFile = File(...)):
    invoice: Invoice = await read_and_save_invoice_firestore(request=request, pdf_file=pdf_file)

    return JSONResponse(content=invoice, status_code=201)

@invoice_router.patch("/updateInvoiceFields/{invoice_id}")
async def partial_update_invoice(request: Request, invoice_id: str, invoice_update_data: InvoicePatchRequest):
    updated_data = await update_invoice_fields_firestore(request=request, invoice_id=invoice_id, invoice_data=invoice_update_data)

    return JSONResponse(content=updated_data, status_code=200)