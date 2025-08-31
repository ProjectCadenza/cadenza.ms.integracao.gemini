from fastapi import FastAPI
from src.config.database import engine
from src.model.orm import Base as invoice_base
from src.controller.invoice import invoice_router
from dotenv import load_dotenv

load_dotenv()

invoice_base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(invoice_router)



