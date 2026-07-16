from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.security.current_device import get_current_device
from app.application.security.access_token_service import (
    AccessToken,
    AccessTokenService,
)
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


class FakeAccessTokenService(AccessTokenService):
    def __init__(
        self,
        device_id: UUID | None = None,
        should_fail: bool = False,
    ) -> None:
        self._device_id = device_id or uuid4()
        self._should_fail = should_fail

    def create_device_access_token(
        self,
        device_id: UUID,
    ) -> AccessToken:
        issued_at = datetime.now(timezone.utc)

        return AccessToken(
            value=f"fake-jwt:{device_id}",
            token_type="bearer",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(minutes=30),
        )

    def validate_device_access_token(
        self,
        token: str,
    ) -> UUID:
        if self._should_fail:
            raise ValueError("Invalid access token.")

        return self._device_id


def make_device(
    status: DeviceStatus = DeviceStatus.ACTIVE,
) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )
    device.status = status

    return device


def bearer_credentials(
    token: str = "valid-token",
) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def test_should_return_authenticated_active_device() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()
    repository.save(device)

    token_service = FakeAccessTokenService(
        device_id=device.device_id
    )

    current_device = get_current_device(
        credentials=bearer_credentials(),
        access_token_service=token_service,
        repository=repository,
    )

    assert current_device.device_id == device.device_id
    assert current_device.status == DeviceStatus.ACTIVE


def test_should_reject_missing_credentials() -> None:
    repository = InMemoryDeviceRepository()
    token_service = FakeAccessTokenService()

    with pytest.raises(HTTPException) as raised:
        get_current_device(
            credentials=None,
            access_token_service=token_service,
            repository=repository,
        )

    assert raised.value.status_code == 401
    assert raised.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


def test_should_reject_invalid_access_token() -> None:
    repository = InMemoryDeviceRepository()
    token_service = FakeAccessTokenService(
        should_fail=True
    )

    with pytest.raises(HTTPException) as raised:
        get_current_device(
            credentials=bearer_credentials(),
            access_token_service=token_service,
            repository=repository,
        )

    assert raised.value.status_code == 401
    assert raised.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


def test_should_reject_unknown_device() -> None:
    repository = InMemoryDeviceRepository()
    token_service = FakeAccessTokenService(
        device_id=uuid4()
    )

    with pytest.raises(HTTPException) as raised:
        get_current_device(
            credentials=bearer_credentials(),
            access_token_service=token_service,
            repository=repository,
        )

    assert raised.value.status_code == 401


@pytest.mark.parametrize(
    "device_status",
    [
        DeviceStatus.PENDING,
        DeviceStatus.BLOCKED,
        DeviceStatus.REVOKED,
        DeviceStatus.EXPIRED,
    ],
)
def test_should_reject_non_active_device(
    device_status: DeviceStatus,
) -> None:
    repository = InMemoryDeviceRepository()
    device = make_device(status=device_status)
    repository.save(device)

    token_service = FakeAccessTokenService(
        device_id=device.device_id
    )

    with pytest.raises(HTTPException) as raised:
        get_current_device(
            credentials=bearer_credentials(),
            access_token_service=token_service,
            repository=repository,
        )

    assert raised.value.status_code == 403
    assert device_status.value in raised.value.detail
