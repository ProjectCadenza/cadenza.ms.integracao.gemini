from google.cloud import storage
from src.config.firestore import bucket, GCS_BUCKET_NAME
import uuid
from datetime import datetime
from src.utils.colored_logger import log
from fastapi import HTTPException
 
def upload_to_firebase_storage(file_bytes: bytes, request_id: str, file_ext: str) -> str:
    """
    Faz o upload de um arquivo (em bytes) para um bucket do Google Cloud Storage.

    Args:
        file_bytes (bytes): O conteúdo do arquivo a ser enviado.
        request_id (str): O ID da requisição.
        bucket_name (str): O nome do seu bucket no GCS (ex: "meu-bucket-de-notas").

    Returns:
        str: O GCS URI do arquivo salvo (ex: "gs://meu-bucket-de-notas/invoices/arquivo.pdf").
    """
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)

    destination_path = f"invoices/{request_id}/file.{file_ext}"

    blob = bucket.blob(destination_path)
    blob.upload_from_string(file_bytes)
    log.info(f"Arquivo salvo no Firebase Storage: {destination_path}")
    
    return destination_path