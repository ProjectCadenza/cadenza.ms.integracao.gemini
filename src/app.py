from fastapi import FastAPI
from src.config.database import engine
from src.model.orm import Base as invoice_base
from src.controller.invoice import invoice_router
from src.middlewares.logging import logging_middleware


invoice_base.metadata.create_all(bind=engine)
app = FastAPI()
app.middleware("http")(logging_middleware)
app.include_router(invoice_router)



