import pytest

from app.domain.enums.device_platform import DevicePlatform


def test_should_expose_supported_device_platforms() -> None:
    assert DevicePlatform.ANDROID.value == "android"
    assert DevicePlatform.ANDROID_TV.value == "android_tv"


def test_should_reject_unsupported_device_platform() -> None:
    with pytest.raises(ValueError):
        DevicePlatform("banana")
