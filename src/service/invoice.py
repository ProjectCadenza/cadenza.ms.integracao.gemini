import os,json, traceback
from src.model.invoice import Invoice
from src.dataclass.invoice import InvoicePatchRequest
from pydantic_ai import Agent, BinaryContent
from src.config.firestore import firestore_db, bucket 
from fastapi import HTTPException, status, Request, UploadFile
from datetime import datetime, timezone, date

from src.service.audit_log import create_audit_log
from src.service.firebase_storage import upload_to_firebase_storage 
from src.utils.colored_logger import log

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

async def read_and_save_invoice_firestore(request: Request, pdf_file: UploadFile) -> dict:
    """
    Processa um arquivo de nota fiscal (PDF, PNG, JPEG, etc.) e salva os dados.
    """
    create_audit_log(request, "INVOICE_PROCESSING_STARTED", "IN_PROGRESS")
    
    try:
        log.info(f"Lendo nota fiscal (Firestore): {request.state.request_id}")

        file_bytes = await pdf_file.read()
        media_type = pdf_file.content_type
        
        if '.' in pdf_file.filename:
            file_ext = pdf_file.filename.split('.')[-1]
        else: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ocorreu um erro interno ao processar a nota fiscal, o arquivo não possui uma extensão"
            )

        raw_file_path = upload_to_firebase_storage(
            file_bytes=file_bytes,
            request_id=str(request.state.request_id),
            file_ext=file_ext,
            media_type=media_type
        )

        invoice_data = await invoice_agent.run(
            [BinaryContent(data=file_bytes, media_type=media_type)] 
        )
        
        invoice_pydantic: Invoice = invoice_data.output
        if invoice_pydantic.products:
            for index, product in enumerate(invoice_pydantic.products):
                product.id = index + 1
        
        invoice_dict = invoice_pydantic.model_dump()
        invoice_dict['raw_file_path'] = raw_file_path
        invoice_dict['created_at'] = datetime.now(timezone.utc).isoformat()
        invoice_dict['original_filename'] = pdf_file.filename 
        invoice_dict['original_media_type'] = media_type 

        json_data = json.dumps(invoice_dict, default=str).encode('utf-8')
        json_file_path = upload_to_firebase_storage(
            file_bytes=json_data,
            request_id=str(request.state.request_id),
            file_ext="json",
            media_type="application/json"
        )
        invoice_dict['json_file_path'] = json_file_path

        log.info("Salvando nota fiscal no Firestore")
        update_time, doc_ref = firestore_db.collection('invoices').add(invoice_dict)
        
        invoice_dict['id'] = doc_ref.id

        create_audit_log(
            request, 
            "INVOICE_CREATED", 
            "SUCCESS", 
            invoice_id=doc_ref.id,
            details={"message": f"Nota fiscal {doc_ref.id} criada com sucesso."}
        )

        return invoice_dict

    except Exception as e:
        create_audit_log(
            request, 
            "INVOICE_CREATED", 
            "FAILURE",
            details={"error": str(e), "traceback": traceback.format_exc()}
        )
        log.error(f"Falha ao processar nota fiscal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno ao processar a nota fiscal: {e}"
        )


async def update_invoice_fields_firestore(request: Request, invoice_id: str, invoice_data: InvoicePatchRequest) -> dict:
    """
    Atualiza campos específicos de uma nota fiscal no Firestore.
    """
    log.info(f"Atualizando nota fiscal no Firestore: {invoice_id}")

    doc_ref = firestore_db.collection('invoices').document(invoice_id)
    
    try:
        invoice_doc = doc_ref.get()
        if not invoice_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nota fiscal com ID {invoice_id} não encontrada."
            )

        updated_data = invoice_data.model_dump(exclude_unset=True)

        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado válido fornecido para atualização."
            )
        
        for key, value in updated_data.items():
            if isinstance(value, (date, datetime)):
                updated_data[key] = value.strftime("%Y-%m-%d")

        updated_data['updated_at'] = datetime.now().isoformat()
        doc_ref.update(updated_data)


        create_audit_log(
            request,
            "INVOICE_UPDATED",
            "SUCCESS",
            invoice_id=invoice_id,
            details={
                "message": "Campos da nota fiscal foram atualizados.",
                "updated_fields": list(updated_data.keys())
            }
        )
        
        log.info(f"Nota fiscal {invoice_id} atualizada com sucesso.")
        return updated_data

    except Exception as e:
        create_audit_log(
            request,
            "INVOICE_UPDATED",
            "FAILURE",
            invoice_id=invoice_id,
            details={"error": str(e)}
        )
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ocorreu um erro interno ao atualizar a nota fiscal: {e}"
            )
        raise e