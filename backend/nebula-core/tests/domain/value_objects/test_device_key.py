import pytest

from app.domain.value_objects.device_key import DeviceKey


def test_should_generate_valid_device_key() -> None:
    device_key = DeviceKey.generate()

    assert isinstance(device_key.value, str)
    assert len(device_key.value) >= DeviceKey.MIN_LENGTH


def test_should_generate_different_device_keys() -> None:
    first_key = DeviceKey.generate()
    second_key = DeviceKey.generate()

    assert first_key != second_key


def test_should_accept_existing_valid_device_key() -> None:
    value = "a" * DeviceKey.MIN_LENGTH

    device_key = DeviceKey(value)

    assert str(device_key) == value


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "short",
        "a" * (DeviceKey.MIN_LENGTH - 1),
    ],
)
def test_should_reject_short_device_key(invalid_value: str) -> None:
    with pytest.raises(ValueError, match="at least"):
        DeviceKey(invalid_value)


def test_should_reject_non_string_device_key() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        DeviceKey(123)  # type: ignore[arg-type]
