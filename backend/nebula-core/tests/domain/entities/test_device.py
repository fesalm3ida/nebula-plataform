from datetime import timedelta

import pytest

from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.license_type import LicenseType
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion


def make_device() -> Device:
    return Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
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


def test_should_grant_trial_on_first_activation() -> None:
    device = make_device()

    device.activate()

    assert device.license_type == LicenseType.TRIAL
    assert device.activated_at is not None
    assert device.license_expires_at is not None
    assert device.license_days_remaining() == Device.TRIAL_DURATION_DAYS - 1
    assert device.is_license_expired() is False


def test_should_not_reset_trial_on_reactivation() -> None:
    device = make_device()
    device.activate()

    expires_at = device.license_expires_at
    activated_at = device.activated_at
    device.block()
    device.activate()

    assert device.license_type == LicenseType.TRIAL
    assert device.license_expires_at == expires_at
    assert device.activated_at == activated_at


def test_should_expire_trial_after_seven_days() -> None:
    device = make_device()
    device.activate()

    later = device.license_expires_at + timedelta(seconds=1)

    assert device.is_license_expired(now=later) is True
    assert device.license_days_remaining(now=later) == 0


def test_should_grant_annual_license() -> None:
    device = make_device()
    device.activate()

    device.grant_license(LicenseType.ANNUAL)

    assert device.license_type == LicenseType.ANNUAL
    assert device.status == DeviceStatus.ACTIVE
    assert device.is_license_expired() is False


def test_should_extend_annual_license_when_still_valid() -> None:
    device = make_device()
    device.activate()
    device.grant_license(LicenseType.ANNUAL)

    first_expiry = device.license_expires_at
    device.grant_license(LicenseType.ANNUAL)

    assert device.license_expires_at == first_expiry + timedelta(
        days=Device.ANNUAL_DURATION_DAYS
    )


def test_should_grant_lifetime_license_without_expiry() -> None:
    device = make_device()
    device.activate()

    device.grant_license(LicenseType.LIFETIME)

    assert device.license_type == LicenseType.LIFETIME
    assert device.license_expires_at is None
    assert device.is_license_expired() is False
    assert device.license_days_remaining() is None


def test_should_reject_trial_through_grant_license() -> None:
    device = make_device()

    with pytest.raises(ValueError):
        device.grant_license(LicenseType.TRIAL)
