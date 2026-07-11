from fastapi import FastAPI


app = FastAPI(
    title="Nebula Core",
    version="0.1.0",
)


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
