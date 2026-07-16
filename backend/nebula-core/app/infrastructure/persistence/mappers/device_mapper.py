from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.persistence.models.device_model import (
    DeviceModel,
)


class DeviceMapper:
    @staticmethod
    def to_model(device: Device) -> DeviceModel:
        return DeviceModel(
            device_id=device.device_id,
            fingerprint=str(device.fingerprint),
            mac_address=str(device.mac_address),
            platform=device.platform.value,
            app_version=str(device.app_version),
            device_key=str(device.device_key),
            status=device.status.value,
            created_at=device.created_at,
        )

    @staticmethod
    def to_domain(model: DeviceModel) -> Device:
        device = Device(
            fingerprint=DeviceFingerprint(model.fingerprint),
            mac_address=MacAddress(model.mac_address),
            platform=DevicePlatform(model.platform),
            app_version=AppVersion(model.app_version),
        )

        device.device_id = model.device_id
        device.device_key = DeviceKey(model.device_key)
        device.status = DeviceStatus(model.status)
        device.created_at = model.created_at

        return device
