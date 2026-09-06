from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)


def make_assignment(
    *,
    device_id: UUID | None = None,
    playlist_id: UUID | None = None,
    status: PlaylistAssignmentStatus = PlaylistAssignmentStatus.ACTIVE,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> PlaylistAssignment:
    now = datetime.now(timezone.utc)

    return PlaylistAssignment(
        device_id=device_id or uuid4(),
        playlist_id=playlist_id or uuid4(),
        status=status,
        created_at=created_at or now,
        updated_at=updated_at or now,
    )


def test_should_create_active_assignment() -> None:
    assignment = make_assignment()

    assert isinstance(assignment.assignment_id, UUID)
    assert assignment.status == PlaylistAssignmentStatus.ACTIVE
    assert assignment.is_active is True


def test_should_revoke_assignment() -> None:
    assignment = make_assignment()
    previous_updated_at = assignment.updated_at

    assignment.revoke()

    assert assignment.status == PlaylistAssignmentStatus.REVOKED
    assert assignment.is_active is False
    assert assignment.updated_at > previous_updated_at


def test_should_reactivate_revoked_assignment() -> None:
    assignment = make_assignment()
    assignment.revoke()

    assignment.reactivate()

    assert assignment.status == PlaylistAssignmentStatus.ACTIVE
    assert assignment.is_active is True


def test_should_not_change_updated_at_when_revoking_twice() -> None:
    assignment = make_assignment()
    assignment.revoke()
    previous_updated_at = assignment.updated_at

    assignment.revoke()

    assert assignment.status == PlaylistAssignmentStatus.REVOKED
    assert assignment.updated_at == previous_updated_at


def test_should_reject_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="created_at must include timezone information",
    ):
        make_assignment(created_at=datetime.now())


def test_should_reject_naive_updated_at() -> None:
    with pytest.raises(
        ValueError,
        match="updated_at must include timezone information",
    ):
        make_assignment(updated_at=datetime.now())


def test_should_reject_updated_at_before_created_at() -> None:
    created_at = datetime.now(timezone.utc)
    updated_at = created_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="updated_at cannot be earlier than created_at",
    ):
        make_assignment(
            created_at=created_at,
            updated_at=updated_at,
        )
