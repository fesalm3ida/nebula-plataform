from fastapi import FastAPI
from app.api.routes.devices import router as devices_router
from app.api.routes.auth import router as auth_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.playlists import router as playlists_router
from app.api.routes.provisioning import router as provisioning_router
from app.api.routes.observability import router as observability_router
from app.api.routes.license import router as license_router
from app.api.routes.portal import router as portal_router
from app.api.routes.payments import router as payments_router
from app.core.config import get_settings


# Valida a configuração já na subida: variável de ambiente faltando (ex.:
# DATABASE_URL) derruba o deploy com mensagem clara, em vez de responder 500
# em cada requisição.
get_settings()

app = FastAPI(
    title="Nebula Core",
    version="0.1.0",
)

app.include_router(devices_router)
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(playlists_router)
app.include_router(provisioning_router)
app.include_router(observability_router)
app.include_router(license_router)
app.include_router(portal_router)
app.include_router(payments_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Nebula Core",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }
