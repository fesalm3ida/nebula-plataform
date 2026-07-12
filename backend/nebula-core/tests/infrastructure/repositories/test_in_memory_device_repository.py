from uuid import uuid4

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


def make_device() -> Device:
    return Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )


def test_should_save_and_find_device_by_id() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()

    repository.save(device)

    assert repository.find_by_id(device.device_id) == device


def test_should_update_existing_device() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()
    repository.save(device)

    device.activate()
    repository.save(device)

    assert repository.find_by_id(device.device_id) == device


def test_should_find_device_by_mac_address() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()
    repository.save(device)

    found_device = repository.find_by_mac_address(device.mac_address)

    assert found_device == device


def test_should_find_device_by_fingerprint() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()
    repository.save(device)

    found_device = repository.find_by_fingerprint(device.fingerprint)

    assert found_device == device


def test_should_find_device_by_device_key() -> None:
    repository = InMemoryDeviceRepository()
    device = make_device()
    repository.save(device)

    found_device = repository.find_by_device_key(device.device_key)

    assert found_device == device


def test_should_return_none_when_device_does_not_exist() -> None:
    repository = InMemoryDeviceRepository()

    assert repository.find_by_id(uuid4()) is None
    assert (
        repository.find_by_mac_address(
            MacAddress("11:22:33:44:55:66")
        )
        is None
    )
    assert (
        repository.find_by_fingerprint(
            DeviceFingerprint("b" * 64)
        )
        is None
    )
    assert (
        repository.find_by_device_key(
            DeviceKey("x" * DeviceKey.MIN_LENGTH)
        )
        is None
    )
