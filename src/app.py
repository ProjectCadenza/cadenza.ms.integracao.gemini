from fastapi import FastAPI
from src.controller.invoice import invoice_router
from src.middlewares.logging import logging_middleware

app = FastAPI()
app.middleware("http")(logging_middleware)
app.include_router(invoice_router)



