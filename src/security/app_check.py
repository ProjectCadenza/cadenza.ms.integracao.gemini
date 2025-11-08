from fastapi import Request, HTTPException, status
from firebase_admin import app_check

async def verify_app_check(request: Request):
    """
    Bloqueia a requisição se o token estiver ausente ou for inválido.
    """
    app_check_token = request.headers.get("X-Firebase-AppCheck")

    if not app_check_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do App Check ausente."
        )

    try:
        app_check.verify_token(app_check_token)
        return
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token do App Check inválido: {e}"
        )