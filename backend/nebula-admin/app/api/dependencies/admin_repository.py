from app.application.security.password_hasher import hash_password
from app.core.config import get_settings
from app.domain.entities.admin import Admin
from app.domain.enums.admin_role import AdminRole
from app.domain.repositories.admin_repository import AdminRepository
from app.infrastructure.admin_store import InMemoryAdminRepository


def get_admin_repository() -> AdminRepository:
    """Fornece o repositório de administradores (bootstrap via configuração)."""

    settings = get_settings()
    admin = Admin(
        email=settings.admin_seed_email,
        password_hash=hash_password(settings.admin_seed_password),
        role=AdminRole(settings.admin_seed_role),
    )

    return InMemoryAdminRepository([admin])
