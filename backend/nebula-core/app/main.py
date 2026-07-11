from fastapi import FastAPI

from app.api.routes.devices import router as devices_router


app = FastAPI(
    title="Nebula Core",
    version="0.1.0",
)

app.include_router(devices_router)


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
