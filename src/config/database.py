import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.colored_logger import log

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    log.info("Obtendo conexão com o banco de dados")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()