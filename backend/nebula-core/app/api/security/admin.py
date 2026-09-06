from fastapi import Header, HTTPException, status

from app.core.config import get_settings


AUTHENTICATE_HEADER = {
    "WWW-Authenticate": "Bearer",
}


def require_admin(
    admin_token: str | None = Header(
        default=None,
        alias="X-Admin-Token",
    ),
) -> None:
    """Guarda das rotas administrativas (placeholder).

    Enquanto o Nebula Admin nao implementa autenticacao e autorizacao de
    administradores, as rotas de gestao exigem um token de administracao
    compartilhado enviado no header ``X-Admin-Token``.
    """

    settings = get_settings()

    if not admin_token or admin_token != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administration credentials.",
            headers=AUTHENTICATE_HEADER,
        )
