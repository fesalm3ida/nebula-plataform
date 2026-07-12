from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.session import Session


class SessionRepository(ABC):
    @abstractmethod
    def save(self, session: Session) -> None:
        """Create or update a Session."""

    @abstractmethod
    def find_by_id(self, session_id: UUID) -> Session | None:
        """Find a Session by its unique identifier."""

    @abstractmethod
    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> Session | None:
        """Find the active Session associated with a Device."""
