from app.infrastructure.persistence.models.session_model import (
    SessionModel,
)


def test_should_map_session_model_to_sessions_table() -> None:
    assert SessionModel.__tablename__ == "sessions"


def test_should_expose_expected_session_columns() -> None:
    columns = SessionModel.__table__.columns

    assert set(columns.keys()) == {
        "session_id",
        "device_id",
        "status",
        "started_at",
        "last_seen",
        "expires_at",
        "ended_at",
    }


def test_should_define_session_id_as_primary_key() -> None:
    session_id_column = SessionModel.__table__.columns["session_id"]

    assert session_id_column.primary_key is True
    assert session_id_column.nullable is False


def test_should_define_device_foreign_key() -> None:
    device_id_column = SessionModel.__table__.columns["device_id"]
    foreign_keys = list(device_id_column.foreign_keys)

    assert device_id_column.nullable is False
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "devices.device_id"
    assert foreign_keys[0].ondelete == "CASCADE"


def test_should_require_session_presence_fields() -> None:
    columns = SessionModel.__table__.columns

    required_columns = [
        "device_id",
        "status",
        "started_at",
        "last_seen",
        "expires_at",
    ]

    for column_name in required_columns:
        assert columns[column_name].nullable is False


def test_should_allow_ended_at_to_be_null() -> None:
    ended_at_column = SessionModel.__table__.columns["ended_at"]

    assert ended_at_column.nullable is True


def test_should_define_session_indexes() -> None:
    index_names = {
        index.name
        for index in SessionModel.__table__.indexes
    }

    assert "ix_sessions_device_status" in index_names
    assert "ix_sessions_status_last_seen" in index_names


def test_should_define_device_relationship() -> None:
    relationship = SessionModel.__mapper__.relationships["device"]

    assert relationship.back_populates == "sessions"
    assert relationship.mapper.class_.__name__ == "DeviceModel"
