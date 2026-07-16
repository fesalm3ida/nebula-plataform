from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.infrastructure.persistence.mappers.session_mapper import (
    SessionMapper,
)
from app.infrastructure.persistence.models.session_model import (
    SessionModel,
)


def make_active_session() -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=uuid4(),
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def test_should_convert_domain_session_to_model() -> None:
    session = make_active_session()

    model = SessionMapper.to_model(session)

    assert isinstance(model, SessionModel)
    assert model.session_id == session.session_id
    assert model.device_id == session.device_id
    assert model.status == session.status.value
    assert model.started_at == session.started_at
    assert model.last_seen == session.last_seen
    assert model.expires_at == session.expires_at
    assert model.ended_at == session.ended_at


def test_should_convert_model_to_domain_session() -> None:
    session = make_active_session()
    session.touch(
        session.started_at + timedelta(seconds=30)
    )

    model = SessionMapper.to_model(session)
    restored = SessionMapper.to_domain(model)

    assert restored.session_id == session.session_id
    assert restored.device_id == session.device_id
    assert restored.status == SessionStatus.ACTIVE
    assert restored.started_at == session.started_at
    assert restored.last_seen == session.last_seen
    assert restored.expires_at == session.expires_at
    assert restored.ended_at is None


def test_should_preserve_ended_session_after_round_trip() -> None:
    session = make_active_session()
    session.end()

    restored = SessionMapper.to_domain(
        SessionMapper.to_model(session)
    )

    assert restored.session_id == session.session_id
    assert restored.status == SessionStatus.ENDED
    assert restored.ended_at == session.ended_at
    assert restored.last_seen == session.last_seen


def test_should_preserve_expired_session_after_round_trip() -> None:
    session = make_active_session()
    session.expire()

    restored = SessionMapper.to_domain(
        SessionMapper.to_model(session)
    )

    assert restored.status == SessionStatus.EXPIRED
    assert restored.ended_at == session.ended_at


def test_should_preserve_session_identity_after_round_trip() -> None:
    original = make_active_session()

    restored = SessionMapper.to_domain(
        SessionMapper.to_model(original)
    )

    assert restored.session_id == original.session_id
    assert restored.device_id == original.device_id
    assert restored.status == original.status
    assert restored.started_at == original.started_at
    assert restored.last_seen == original.last_seen
    assert restored.expires_at == original.expires_at
