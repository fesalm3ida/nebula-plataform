from fastapi import FastAPI
from app.api.routes.devices import router as devices_router
from app.api.routes.auth import router as auth_router


app = FastAPI(
    title="Nebula Core",
    version="0.1.0",
)

app.include_router(devices_router)
app.include_router(auth_router)


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
