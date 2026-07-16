from app.infrastructure.persistence.models.device_model import (
    DeviceModel,
)


def test_should_map_device_model_to_devices_table() -> None:
    assert DeviceModel.__tablename__ == "devices"


def test_should_expose_expected_device_columns() -> None:
    columns = DeviceModel.__table__.columns

    assert set(columns.keys()) == {
        "device_id",
        "fingerprint",
        "mac_address",
        "platform",
        "app_version",
        "device_key",
        "status",
        "created_at",
    }


def test_should_define_device_id_as_primary_key() -> None:
    device_id_column = DeviceModel.__table__.columns["device_id"]

    assert device_id_column.primary_key is True
    assert device_id_column.nullable is False


def test_should_define_unique_device_identity_columns() -> None:
    columns = DeviceModel.__table__.columns

    assert columns["fingerprint"].unique is True
    assert columns["mac_address"].unique is True
    assert columns["device_key"].unique is True


def test_should_require_core_device_fields() -> None:
    columns = DeviceModel.__table__.columns

    required_columns = [
        "fingerprint",
        "mac_address",
        "platform",
        "app_version",
        "device_key",
        "status",
        "created_at",
    ]

    for column_name in required_columns:
        assert columns[column_name].nullable is False


def test_should_define_platform_status_index() -> None:
    index_names = {
        index.name
        for index in DeviceModel.__table__.indexes
    }

    assert "ix_devices_platform_status" in index_names
