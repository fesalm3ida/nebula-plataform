import pytest
from pydantic import ValidationError

from app.api.schemas.device_registration import DeviceRegistrationRequest


def test_should_accept_valid_device_registration_request() -> None:
    request = DeviceRegistrationRequest(
        fingerprint="a" * 64,
        mac_address="AA:BB:CC:DD:EE:FF",
        platform="android_tv",
        app_version="0.1.0",
    )

    assert request.fingerprint == "a" * 64


@pytest.mark.parametrize(
    "invalid_fingerprint",
    [
        "",
        "a" * 63,
        "a" * 65,
    ],
)
def test_should_reject_invalid_fingerprint_length(
    invalid_fingerprint: str,
) -> None:
    with pytest.raises(ValidationError):
        DeviceRegistrationRequest(
            fingerprint=invalid_fingerprint,
            mac_address="AA:BB:CC:DD:EE:FF",
            platform="android_tv",
            app_version="0.1.0",
        )
