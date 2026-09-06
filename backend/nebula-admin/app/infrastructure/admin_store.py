from uuid import UUID

from app.domain.entities.admin import Admin
from app.domain.repositories.admin_repository import AdminRepository


class InMemoryAdminRepository(AdminRepository):
    """Repositório de administradores em memória (bootstrap via config).

    Segue o princípio YAGNI: uma tabela de administradores em banco fica para
    depois; o Admin não possui persistência de dados do Core.
    """

    def __init__(self, admins: list[Admin] | None = None) -> None:
        self._admins: dict[UUID, Admin] = {}

        for admin in admins or []:
            self._admins[admin.admin_id] = admin

    def save(self, admin: Admin) -> None:
        self._admins[admin.admin_id] = admin

    def find_by_email(self, email: str) -> Admin | None:
        normalized = email.strip().lower()

        for admin in self._admins.values():
            if admin.email == normalized:
                return admin

        return None

    def find_by_id(self, admin_id: UUID) -> Admin | None:
        return self._admins.get(admin_id)
