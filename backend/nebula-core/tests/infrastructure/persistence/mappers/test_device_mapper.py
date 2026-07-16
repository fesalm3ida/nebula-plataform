from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.persistence.mappers.device_mapper import (
    DeviceMapper,
)
from app.infrastructure.persistence.models.device_model import (
    DeviceModel,
)


def make_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )

    device.activate()

    return device


def test_should_convert_domain_device_to_model() -> None:
    device = make_device()

    model = DeviceMapper.to_model(device)

    assert isinstance(model, DeviceModel)

    assert model.device_id == device.device_id
    assert model.fingerprint == str(device.fingerprint)
    assert model.mac_address == str(device.mac_address)
    assert model.platform == device.platform.value
    assert model.app_version == str(device.app_version)
    assert model.device_key == str(device.device_key)
    assert model.status == device.status.value
    assert model.created_at == device.created_at


def test_should_convert_model_to_domain_device() -> None:
    device = make_device()

    model = DeviceMapper.to_model(device)

    restored = DeviceMapper.to_domain(model)

    assert restored.device_id == device.device_id
    assert restored.fingerprint == device.fingerprint
    assert restored.mac_address == device.mac_address
    assert restored.platform == device.platform
    assert restored.app_version == device.app_version
    assert restored.device_key == device.device_key
    assert restored.status == DeviceStatus.ACTIVE
    assert restored.created_at == device.created_at


def test_should_preserve_identity_after_round_trip() -> None:
    original = make_device()

    restored = DeviceMapper.to_domain(
        DeviceMapper.to_model(original)
    )

    assert restored.device_id == original.device_id
    assert restored.fingerprint == original.fingerprint
    assert restored.mac_address == original.mac_address
    assert restored.device_key == original.device_key
    assert restored.status == original.status
