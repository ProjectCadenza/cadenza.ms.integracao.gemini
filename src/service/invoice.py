from src.model.invoice import Invoice
from pydantic_ai import Agent, BinaryContent
from src.model.orm import InvoiceDB, ProductDB
from dotenv import load_dotenv
from src.config.database import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.model.orm import InvoiceDB
from src.dataclass.invoice import InvoicePatchRequest

load_dotenv()

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

async def read_and_save_invoice(pdf_file: bytes) -> Invoice:
    invoice_data = await invoice_agent.run(
        [
            BinaryContent(data=pdf_file, media_type='application/pdf')
        ]
    )
    invoice_pydantic: Invoice = invoice_data.output

    db: Session = next(get_db())

    try:
        new_invoice_db = InvoiceDB(**invoice_pydantic.model_dump(exclude={'products'}))
        
        if invoice_pydantic.products:
            for p_pydantic in invoice_pydantic.products:
                p_db = ProductDB(**p_pydantic.model_dump())
                new_invoice_db.products.append(p_db)

        db.add(new_invoice_db)
        db.commit()
        db.refresh(new_invoice_db)

        return invoice_pydantic
    
    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()

def update_invoice_fields(invoice_id: int, invoice_data: InvoicePatchRequest) -> InvoiceDB:
    db: Session = next(get_db())
    db_invoice = db.query(InvoiceDB).filter(InvoiceDB.id == invoice_id).first()

    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nota fiscal com ID {invoice_id} não encontrada."
        )

    update_data = invoice_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_invoice, key, value)

    db.commit()
    db.refresh(db_invoice)

    return update_data