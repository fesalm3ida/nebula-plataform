from uuid import uuid4

from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.infrastructure.repositories.in_memory_playlist_assignment_repository import (
    InMemoryPlaylistAssignmentRepository,
)


def make_assignment(
    *,
    device_id=None,
    playlist_id=None,
) -> PlaylistAssignment:
    return PlaylistAssignment(
        device_id=device_id or uuid4(),
        playlist_id=playlist_id or uuid4(),
    )


def test_should_save_and_find_active_assignment_for_device() -> None:
    repository = InMemoryPlaylistAssignmentRepository()
    device_id = uuid4()
    assignment = make_assignment(device_id=device_id)

    repository.save(assignment)

    restored = repository.find_active_by_device_id(device_id)

    assert restored is not None
    assert restored.assignment_id == assignment.assignment_id
    assert restored.playlist_id == assignment.playlist_id


def test_should_ignore_revoked_assignment_for_device() -> None:
    repository = InMemoryPlaylistAssignmentRepository()
    device_id = uuid4()
    assignment = make_assignment(device_id=device_id)
    assignment.revoke()

    repository.save(assignment)

    assert repository.find_active_by_device_id(device_id) is None


def test_should_return_none_for_device_without_assignment() -> None:
    repository = InMemoryPlaylistAssignmentRepository()

    assert repository.find_active_by_device_id(uuid4()) is None
