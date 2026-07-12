import pytest

from app.domain.value_objects.mac_address import MacAddress


def test_should_accept_valid_mac_address() -> None:
    mac_address = MacAddress("AA:BB:CC:DD:EE:FF")

    assert mac_address.value == "AA:BB:CC:DD:EE:FF"
    assert str(mac_address) == "AA:BB:CC:DD:EE:FF"


def test_should_normalize_mac_address_to_uppercase() -> None:
    mac_address = MacAddress("aa:bb:cc:dd:ee:ff")

    assert mac_address.value == "AA:BB:CC:DD:EE:FF"


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "123",
        "AA:BB:CC:DD:EE",
        "AA:BB:CC:DD:EE:GG",
        "AA-BB-CC-DD-EE-FF",
    ],
)
def test_should_reject_invalid_mac_address(invalid_value: str) -> None:
    with pytest.raises(ValueError, match="Invalid MAC address format"):
        MacAddress(invalid_value)
