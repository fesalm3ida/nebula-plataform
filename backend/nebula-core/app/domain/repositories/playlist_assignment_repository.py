from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.playlist_assignment import PlaylistAssignment


class PlaylistAssignmentRepository(ABC):
    @abstractmethod
    def save(self, assignment: PlaylistAssignment) -> None:
        """Create or update a PlaylistAssignment."""

    @abstractmethod
    def find_by_id(
        self,
        assignment_id: UUID,
    ) -> PlaylistAssignment | None:
        """Find a PlaylistAssignment by its unique identifier."""

    @abstractmethod
    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> PlaylistAssignment | None:
        """Find the active PlaylistAssignment for a given Device."""

    @abstractmethod
    def find_all_active_by_device_id(
        self,
        device_id: UUID,
    ) -> list[PlaylistAssignment]:
        """Return all active PlaylistAssignments for a given Device."""
