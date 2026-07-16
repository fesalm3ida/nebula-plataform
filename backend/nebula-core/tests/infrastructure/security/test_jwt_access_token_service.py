from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.application.security.access_token_service import AccessToken
from app.infrastructure.security.jwt_access_token_service import (
    JWTAccessTokenService,
)


SECRET_KEY = "test-secret-key-with-at-least-thirty-two-characters"
ISSUER = "nebula-core"
AUDIENCE = "nebula-player"
ALGORITHM = "HS256"


def make_service(
    secret_key: str = SECRET_KEY,
    audience: str = AUDIENCE,
) -> JWTAccessTokenService:
    return JWTAccessTokenService(
        secret_key=secret_key,
        issuer=ISSUER,
        audience=audience,
        algorithm=ALGORITHM,
        expiration_minutes=30,
    )


def test_should_create_and_validate_device_access_token() -> None:
    service = make_service()
    device_id = uuid4()

    access_token = service.create_device_access_token(
        device_id
    )

    authenticated_device_id = (
        service.validate_device_access_token(
            access_token.value
        )
    )

    assert isinstance(access_token, AccessToken)
    assert access_token.token_type == "bearer"
    assert access_token.issued_at.tzinfo is not None
    assert access_token.expires_at > access_token.issued_at
    assert authenticated_device_id == device_id


def test_should_include_required_claims() -> None:
    service = make_service()
    device_id = uuid4()

    access_token = service.create_device_access_token(
        device_id
    )

    payload = jwt.decode(
        access_token.value,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=ISSUER,
        audience=AUDIENCE,
    )

    assert payload["iss"] == ISSUER
    assert payload["sub"] == f"device:{device_id}"
    assert payload["aud"] == AUDIENCE
    assert payload["device_id"] == str(device_id)
    assert payload["token_type"] == "access"
    assert payload["jti"]
    assert payload["iat"]
    assert payload["nbf"]
    assert payload["exp"]


def test_should_reject_token_with_invalid_signature() -> None:
    issuing_service = make_service()
    validating_service = make_service(
        secret_key="another-secret-key-with-enough-characters"
    )

    access_token = (
        issuing_service.create_device_access_token(
            uuid4()
        )
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        validating_service.validate_device_access_token(
            access_token.value
        )


def test_should_reject_token_with_invalid_audience() -> None:
    issuing_service = make_service()
    validating_service = make_service(
        audience="nebula-admin"
    )

    access_token = (
        issuing_service.create_device_access_token(
            uuid4()
        )
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        validating_service.validate_device_access_token(
            access_token.value
        )


def test_should_reject_expired_access_token() -> None:
    service = make_service()
    device_id = uuid4()
    now = datetime.now(timezone.utc)

    payload = {
        "iss": ISSUER,
        "sub": f"device:{device_id}",
        "aud": AUDIENCE,
        "iat": now - timedelta(minutes=31),
        "nbf": now - timedelta(minutes=31),
        "exp": now - timedelta(minutes=1),
        "jti": str(uuid4()),
        "device_id": str(device_id),
        "token_type": "access",
    }

    expired_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        service.validate_device_access_token(
            expired_token
        )


def test_should_reject_token_with_invalid_type() -> None:
    service = make_service()
    device_id = uuid4()
    now = datetime.now(timezone.utc)

    payload = {
        "iss": ISSUER,
        "sub": f"device:{device_id}",
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=30),
        "jti": str(uuid4()),
        "device_id": str(device_id),
        "token_type": "refresh",
    }

    refresh_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        service.validate_device_access_token(
            refresh_token
        )
