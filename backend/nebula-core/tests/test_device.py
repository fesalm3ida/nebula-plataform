from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress


def make_device() -> Device:
    return Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform="android_tv",
        app_version="0.1.0",
    )


def test_should_create_device_as_pending() -> None:
    device = make_device()

    assert device.status == DeviceStatus.PENDING
    assert device.device_id is not None
    assert device.device_key is not None
    assert device.created_at is not None


def test_should_activate_device() -> None:
    device = make_device()

    device.activate()

    assert device.status == DeviceStatus.ACTIVE


def test_should_block_device() -> None:
    device = make_device()

    device.block()

    assert device.status == DeviceStatus.BLOCKED


def test_should_revoke_device() -> None:
    device = make_device()

    device.revoke()

    assert device.status == DeviceStatus.REVOKED


def test_should_expire_device() -> None:
    device = make_device()

    device.expire()

    assert device.status == DeviceStatus.EXPIRED
