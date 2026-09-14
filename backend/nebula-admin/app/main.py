from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as admin_auth_router
from app.api.routes.devices import router as admin_devices_router
from app.api.routes.playlists import router as admin_playlists_router
from app.api.routes.portal import router as portal_router


app = FastAPI(
    title="Nebula Admin",
    version="0.1.0",
)

# CORS para o Flutter Admin (Web) consumir a API. Em desenvolvimento permite
# qualquer origem; em produção restrinja ao dominio do Flutter Web.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth_router)
app.include_router(admin_devices_router)
app.include_router(admin_playlists_router)
app.include_router(portal_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Nebula Admin",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }
