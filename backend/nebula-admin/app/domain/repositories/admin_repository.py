from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.admin import Admin


class AdminRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Admin | None:
        """Find an Admin by its email."""

    @abstractmethod
    def find_by_id(self, admin_id: UUID) -> Admin | None:
        """Find an Admin by its identifier."""
