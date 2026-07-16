from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.api.dependencies.session_repository import (
    get_session_repository,
)
from app.api.security.current_device import get_current_device
from app.domain.entities.device import Device
from app.domain.entities.session import Session
from app.domain.repositories.session_repository import (
    SessionRepository,
)


def get_current_session(
    session_id: UUID,
    current_device: Device = Depends(
        get_current_device
    ),
    repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> Session:
    """Resolve a Session owned by the authenticated Device."""

    session = repository.find_by_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    if session.device_id != current_device.device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Authenticated Device is not authorized "
                "to access this Session."
            ),
        )

    return session
