from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.log_repository import get_log_repository
from app.api.dependencies.session_repository import get_session_repository
from app.api.dependencies.telemetry_event_repository import (
    get_telemetry_event_repository,
)
from app.api.schemas.observability import (
    LogRequest,
    LogResponse,
    TelemetryEventRequest,
    TelemetryEventResponse,
)
from app.api.security.current_device import get_current_device
from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
    SessionOwnershipError,
)
from app.application.use_cases.ingest_log import (
    IngestLogCommand,
    IngestLogUseCase,
)
from app.application.use_cases.ingest_telemetry_event import (
    IngestTelemetryEventCommand,
    IngestTelemetryEventUseCase,
)
from app.domain.entities.device import Device
from app.domain.repositories.log_repository import LogRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)


router = APIRouter(
    tags=["Observability"],
)


@router.post(
    "/me/telemetry",
    response_model=TelemetryEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Telemetry Event",
    description=(
        "Records a telemetry event for a Session owned by the "
        "authenticated Device (ADR-022/023)."
    ),
)
def ingest_telemetry_event(
    payload: TelemetryEventRequest,
    current_device: Device = Depends(get_current_device),
    telemetry_repository: TelemetryEventRepository = Depends(
        get_telemetry_event_repository
    ),
    session_repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> TelemetryEventResponse:
    use_case = IngestTelemetryEventUseCase(
        telemetry_event_repository=telemetry_repository,
        session_repository=session_repository,
    )

    try:
        result = use_case.execute(
            IngestTelemetryEventCommand(
                device_id=current_device.device_id,
                session_id=payload.session_id,
                event_type=payload.event_type,
                payload=payload.payload,
                occurred_at=payload.occurred_at,
            )
        )

    except SessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except SessionOwnershipError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except SessionNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return TelemetryEventResponse(
        event_id=result.event_id,
        session_id=payload.session_id,
        device_id=current_device.device_id,
        event_type=payload.event_type,
        occurred_at=result.occurred_at,
        received_at=result.received_at,
    )


@router.post(
    "/me/logs",
    response_model=LogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Log",
    description=(
        "Records a diagnostic log for a Session owned by the "
        "authenticated Device (ADR-022)."
    ),
)
def ingest_log(
    payload: LogRequest,
    current_device: Device = Depends(get_current_device),
    log_repository: LogRepository = Depends(get_log_repository),
    session_repository: SessionRepository = Depends(
        get_session_repository
    ),
) -> LogResponse:
    use_case = IngestLogUseCase(
        log_repository=log_repository,
        session_repository=session_repository,
    )

    try:
        result = use_case.execute(
            IngestLogCommand(
                device_id=current_device.device_id,
                session_id=payload.session_id,
                level=payload.level,
                message=payload.message,
                occurred_at=payload.occurred_at,
            )
        )

    except SessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except SessionOwnershipError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except SessionNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return LogResponse(
        log_id=result.log_id,
        session_id=payload.session_id,
        device_id=current_device.device_id,
        level=payload.level,
        occurred_at=result.occurred_at,
        received_at=result.received_at,
    )
