from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.device_repository import get_device_repository
from app.api.dependencies.session_repository import get_session_repository
from app.api.schemas.session import (
    StartSessionRequest,
    StartSessionResponse,
)
from app.api.schemas.session_heartbeat import SessionHeartbeatResponse
from app.api.schemas.session_termination import EndSessionResponse
from app.application.exceptions import (
    ActiveSessionAlreadyExistsError,
    DeviceNotActiveError,
    DeviceNotFoundError,
    SessionAlreadyClosedError,
    SessionNotActiveError,
    SessionNotFoundError,
)
from app.application.use_cases.end_session import (
    EndSessionCommand,
    EndSessionUseCase,
)
from app.application.use_cases.heartbeat_session import (
    HeartbeatSessionCommand,
    HeartbeatSessionUseCase,
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
        last_seen=result.last_seen,
    )


@router.post(
    "/{session_id}/heartbeat",
    response_model=SessionHeartbeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Session Heartbeat",
    description="Updates the presence timestamp of an active Session.",
)
def heartbeat_session(
    session_id: UUID,
    repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> SessionHeartbeatResponse:
    use_case = HeartbeatSessionUseCase(repository)

    try:
        result = use_case.execute(
            HeartbeatSessionCommand(
                session_id=session_id,
            )
        )

    except SessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except SessionNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return SessionHeartbeatResponse(
        session_id=result.session_id,
        status=result.status,
        last_seen=result.last_seen,
    )


@router.post(
    "/{session_id}/end",
    response_model=EndSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="End Session",
    description="Ends an active Session.",
)
def end_session(
    session_id: UUID,
    repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> EndSessionResponse:
    use_case = EndSessionUseCase(repository)

    try:
        result = use_case.execute(
            EndSessionCommand(session_id=session_id)
        )

    except SessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except SessionAlreadyClosedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return EndSessionResponse(
        session_id=result.session_id,
        status=result.status,
        ended_at=result.ended_at,
    )
