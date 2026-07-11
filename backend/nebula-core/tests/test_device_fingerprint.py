import pytest

from app.domain.value_objects.device_fingerprint import DeviceFingerprint


def test_should_accept_valid_device_fingerprint() -> None:
    value = "a" * 64

    fingerprint = DeviceFingerprint(value)

    assert fingerprint.value == value
    assert str(fingerprint) == value


def test_should_normalize_device_fingerprint() -> None:
    value = ("AB" * 32)

    fingerprint = DeviceFingerprint(f"  {value}  ")

    assert fingerprint.value == value.lower()


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "abc123",
        "a" * 63,
        "a" * 65,
        "g" * 64,
        "aa:bb:cc",
    ],
)
def test_should_reject_invalid_device_fingerprint(
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match="64-character hexadecimal"):
        DeviceFingerprint(invalid_value)


def test_should_reject_non_string_device_fingerprint() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        DeviceFingerprint(123)  # type: ignore[arg-type]
