import os, json
from src.model.invoice import Invoice
from pydantic_ai import Agent, BinaryContent
from src.model.orm import InvoiceDB, ProductDB
from src.config.database import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.model.orm import InvoiceDB
from src.dataclass.invoice import InvoicePatchRequest
from src.service.gcs import upload_to_gcs
from src.service.audit_log import log_audit
from src.utils.colored_logger import log
from fastapi import Request

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

invoice_agent = Agent(
    model='google-gla:gemini-2.5-flash',
    output_type=Invoice,
    system_prompt = (
        'You are an expert invoice reader. Your sole task is to '
        'extract key details from the provided invoice file and map '
        'them to the specified fields of the output structure. '
        'Fill in all possible fields and use a null value for any information not found. '
        'Ensure the output is clean and free of any extra text or conversational phrases.'
    )
)

async def read_and_save_invoice(request: Request, pdf_file: bytes) -> Invoice:
    request_id = request.state.request_id
    log.info(f"Lendo nota fiscal: {request_id}")

    
    raw_gcs_path = upload_to_gcs(
        file_bytes=pdf_file,
        bucket_name=GCS_BUCKET_NAME,
        request_id=request_id,
        file_ext="pdf"
    )

    invoice_data = await invoice_agent.run(
        [
            BinaryContent(data=pdf_file, media_type='application/pdf')
        ]
    )
    invoice_pydantic: Invoice = invoice_data.output
    invoice_dict = invoice_pydantic.model_dump(exclude={'products'})
    invoice_dict['raw_file_uri'] = raw_gcs_path

    json_data = json.dumps(invoice_pydantic.model_dump())
    file_bytes = json_data.encode('utf-8') 

    json_gcs_path = upload_to_gcs(
        file_bytes=file_bytes,
        bucket_name=GCS_BUCKET_NAME,
        request_id=request_id,
        file_ext="json"
    )
    invoice_dict['json_file_uri'] = json_gcs_path

    db: Session = next(get_db())

    try:
        log.info("Salvando nota fiscal no banco de dados")
        invoice_db = InvoiceDB(**invoice_dict)
        
        if invoice_pydantic.products:
            for p_pydantic in invoice_pydantic.products:
                p_db = ProductDB(**p_pydantic.model_dump())
                invoice_db.products.append(p_db)

        db.add(invoice_db)
        db.commit()
        db.refresh(invoice_db)

        log_audit(
            db=db,
            invoice=invoice_db,
            request=request
        )

        return invoice_pydantic.model_dump()
    
    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()

async def update_invoice_fields(request: Request, invoice_id: int, invoice_data: InvoicePatchRequest) -> dict:
    db: Session = next(get_db())
    invoice_db = db.query(InvoiceDB).filter(InvoiceDB.id == invoice_id).first()

    if not invoice_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nota fiscal com ID {invoice_id} não encontrada."
        )

    updated_data = invoice_data.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(invoice_db, key, value)

    db.commit()
    db.refresh(invoice_db)

    log_audit(
        db=db,
        invoice=invoice_db,
        request=request
    )

    return updated_data