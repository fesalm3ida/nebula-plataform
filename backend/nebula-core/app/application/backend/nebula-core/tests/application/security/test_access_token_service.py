from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.application.security.access_token_service import (
    AccessToken,
    AccessTokenService,
)


class FakeAccessTokenService(AccessTokenService):
    def create_device_access_token(
        self,
        device_id: UUID,
    ) -> AccessToken:
        issued_at = datetime.now(timezone.utc)

        return AccessToken(
            value=f"fake-token:{device_id}",
            token_type="bearer",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(minutes=30),
        )

    def validate_device_access_token(
        self,
        token: str,
    ) -> UUID:
        prefix = "fake-token:"

        if not token.startswith(prefix):
            raise ValueError("Invalid access token.")

        raw_device_id = token.removeprefix(prefix)

        return UUID(raw_device_id)


def test_should_create_device_access_token() -> None:
    service = FakeAccessTokenService()
    device_id = uuid4()

    token = service.create_device_access_token(device_id)

    assert isinstance(token, AccessToken)
    assert token.value == f"fake-token:{device_id}"
    assert token.token_type == "bearer"
    assert token.issued_at.tzinfo is not None
    assert token.expires_at > token.issued_at


def test_should_validate_device_access_token() -> None:
    service = FakeAccessTokenService()
    device_id = uuid4()

    token = service.create_device_access_token(device_id)

    authenticated_device_id = (
        service.validate_device_access_token(token.value)
    )

    assert authenticated_device_id == device_id


def test_should_reject_invalid_access_token() -> None:
    service = FakeAccessTokenService()

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        service.validate_device_access_token(
            "invalid-token"
        )


def test_should_reject_invalid_device_identifier_in_token() -> None:
    service = FakeAccessTokenService()

    with pytest.raises(ValueError):
        service.validate_device_access_token(
            "fake-token:not-a-uuid"
        )
