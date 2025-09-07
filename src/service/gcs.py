from google.cloud import storage
import uuid
from datetime import datetime
from src.utils.colored_logger import log
from fastapi import HTTPException
 
def upload_to_gcs(file_bytes: bytes, file_ext: str, bucket_name: str, request_id: str) -> str:
    """
    Faz o upload de um arquivo (em bytes) para um bucket do Google Cloud Storage.

    Args:
        file_bytes (bytes): O conteúdo do arquivo a ser enviado.
        bucket_name (str): O nome do seu bucket no GCS (ex: "meu-bucket-de-notas").

    Returns:
        str: O GCS URI do arquivo salvo (ex: "gs://meu-bucket-de-notas/invoices/arquivo.pdf").
    """
    log.info(f"Carregando arquivo {file_ext.upper()} no GCS: {request_id}")
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        file_name = f"invoices/{file_ext}/{datetime.now().strftime('%Y-%m-%d')}/{request_id}.{file_ext}"
        blob = bucket.blob(file_name)

        blob.upload_from_string(file_bytes, content_type=f"application/{file_ext}")
        log.info(f"Arquivo {file_name} salvo com sucesso no bucket {bucket_name}.")

        return f"gs://{bucket_name}/{file_name}"

    except Exception as e:
        log.error(f"Erro ao fazer upload para o GCS: {e}")
        raise HTTPException(status_code=500, detail="Erro ao fazer upload para o GCS")