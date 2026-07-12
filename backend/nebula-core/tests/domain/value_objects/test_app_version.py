import pytest

from app.domain.value_objects.app_version import AppVersion


@pytest.mark.parametrize(
    "valid_value",
    [
        "0.1.0",
        "1.0.0",
        "10.25.300",
        "1.0.0-beta",
        "2.1.3-rc.1",
    ],
)
def test_should_accept_valid_app_version(valid_value: str) -> None:
    app_version = AppVersion(valid_value)

    assert app_version.value == valid_value
    assert str(app_version) == valid_value


def test_should_trim_app_version() -> None:
    app_version = AppVersion("  1.0.0  ")

    assert app_version.value == "1.0.0"


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "1",
        "1.0",
        "version-1",
        "banana",
    ],
)
def test_should_reject_invalid_app_version(invalid_value: str) -> None:
    with pytest.raises(ValueError, match="semantic versioning"):
        AppVersion(invalid_value)


def test_should_reject_non_string_app_version() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        AppVersion(100)  # type: ignore[arg-type]
