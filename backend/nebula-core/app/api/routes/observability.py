from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.log_repository import get_log_repository
from app.api.dependencies.session_repository import get_session_repository
from app.api.dependencies.telemetry_event_repository import (
    get_telemetry_event_repository,
)
from app.api.schemas.observability import (
    HourlyPoint,
    LogListResponse,
    LogRequest,
    LogResponse,
    LogSummary,
    ObservabilitySummaryResponse,
    TelemetryEventListResponse,
    TelemetryEventRequest,
    TelemetryEventResponse,
    TelemetryEventSummary,
)
from app.api.security.admin import require_admin
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
from app.application.use_cases.get_observability_summary import (
    GetObservabilitySummaryUseCase,
)
from app.application.use_cases.ingest_telemetry_event import (
    IngestTelemetryEventCommand,
    IngestTelemetryEventUseCase,
)
from app.application.use_cases.list_logs import (
    ListLogsCommand,
    ListLogsUseCase,
)
from app.application.use_cases.list_telemetry_events import (
    ListTelemetryEventsCommand,
    ListTelemetryEventsUseCase,
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


@router.get(
    "/observability/summary",
    response_model=ObservabilitySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Observability Summary",
    description=(
        "Resumo para o Nebula Monitor: totais, distribuicao por tipo/nivel e "
        "a serie temporal por hora. Restrito ao administrador."
    ),
    dependencies=[Depends(require_admin)],
)
def get_observability_summary(
    hours: int = Query(default=24, ge=1, le=720),
    telemetry_repository: TelemetryEventRepository = Depends(
        get_telemetry_event_repository
    ),
    log_repository: LogRepository = Depends(get_log_repository),
) -> ObservabilitySummaryResponse:
    summary = GetObservabilitySummaryUseCase(
        telemetry_repository=telemetry_repository,
        log_repository=log_repository,
    ).execute(hours=hours)

    return ObservabilitySummaryResponse(
        since=summary.since,
        total_events=summary.total_events,
        events_by_type=summary.events_by_type,
        events_per_hour=[
            HourlyPoint(hour=hour, count=count)
            for hour, count in summary.events_per_hour
        ],
        total_logs=summary.total_logs,
        logs_by_level=summary.logs_by_level,
    )


@router.get(
    "/observability/telemetry",
    response_model=TelemetryEventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Telemetry Events",
    description=(
        "Eventos de telemetria mais recentes, com filtros. "
        "Restrito ao administrador."
    ),
    dependencies=[Depends(require_admin)],
)
def list_telemetry_events(
    device_id: UUID | None = None,
    event_type: str | None = None,
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=500),
    repository: TelemetryEventRepository = Depends(
        get_telemetry_event_repository
    ),
) -> TelemetryEventListResponse:
    events = ListTelemetryEventsUseCase(repository).execute(
        ListTelemetryEventsCommand(
            device_id=device_id,
            event_type=event_type,
            hours=hours,
            limit=limit,
        )
    )

    return TelemetryEventListResponse(
        events=[
            TelemetryEventSummary(
                event_id=event.event_id,
                device_id=event.device_id,
                session_id=event.session_id,
                event_type=event.event_type.value,
                payload=event.payload,
                occurred_at=event.occurred_at,
            )
            for event in events
        ]
    )


@router.get(
    "/observability/logs",
    response_model=LogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Logs",
    description=(
        "Logs tecnicos mais recentes, com filtros. Restrito ao administrador."
    ),
    dependencies=[Depends(require_admin)],
)
def list_logs(
    device_id: UUID | None = None,
    level: str | None = None,
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=500),
    repository: LogRepository = Depends(get_log_repository),
) -> LogListResponse:
    logs = ListLogsUseCase(repository).execute(
        ListLogsCommand(
            device_id=device_id,
            level=level,
            hours=hours,
            limit=limit,
        )
    )

    return LogListResponse(
        logs=[
            LogSummary(
                log_id=log.log_id,
                device_id=log.device_id,
                session_id=log.session_id,
                level=log.level.value,
                message=log.message,
                occurred_at=log.occurred_at,
            )
            for log in logs
        ]
    )
