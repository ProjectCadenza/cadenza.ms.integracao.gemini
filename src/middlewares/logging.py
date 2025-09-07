import time
import uuid
from fastapi import Request
from src.utils.colored_logger import log

async def logging_middleware(request: Request, call_next):
    """Middleware para logar requisições com request_id"""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    log.info(f"[{request_id}] ➡️ {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    log.info(
        f"[{request_id}] ⬅️ Status: {response.status_code} "
        f"Tempo: {process_time:.2f}ms"
    )

    response.headers["X-Request-ID"] = request_id

    return response
