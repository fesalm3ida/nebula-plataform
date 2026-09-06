from fastapi.security import HTTPBearer


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="AdminBearerAuth",
    description="Administrative Bearer token.",
)
