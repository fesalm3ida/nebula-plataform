from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.device_repository import get_device_repository
from app.api.dependencies.session_repository import get_session_repository
from app.api.schemas.session import (
    StartSessionRequest,
    StartSessionResponse,
)
from app.application.exceptions import (
    ActiveSessionAlreadyExistsError,
    DeviceNotActiveError,
    DeviceNotFoundError,
)
from app.application.use_cases.start_session import (
    StartSessionCommand,
    StartSessionUseCase,
)
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.session_repository import SessionRepository

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post(
    "",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Session",
    description="Starts a new Session for an active Device.",
)
def start_session(
    request: StartSessionRequest,
    device_repository: DeviceRepository = Depends(
        get_device_repository
    ),
    session_repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> StartSessionResponse:
    use_case = StartSessionUseCase(
        device_repository=device_repository,
        session_repository=session_repository,
    )

    try:
        result = use_case.execute(
            StartSessionCommand(
                device_id=request.device_id,
            )
        )

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except DeviceNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except ActiveSessionAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return StartSessionResponse(
        session_id=result.session_id,
        device_id=result.device_id,
        status=result.status,
        started_at=result.started_at,
        expires_at=result.expires_at,
    )
