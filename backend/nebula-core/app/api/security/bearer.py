from fastapi.security import HTTPBearer


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="DeviceBearer",
    description=(
        "JWT access token issued by the Nebula Core "
        "for an authenticated Device."
    ),
)
