from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.api.schemas.monitor import (
    MonitorHourlyPoint,
    MonitorLogOut,
    MonitorLogsResponse,
    MonitorSummaryResponse,
    MonitorTelemetryEventOut,
    MonitorTelemetryResponse,
)
from app.api.security.current_admin import get_current_admin
from app.application.exceptions import (
    CoreAuthenticationError,
    CoreCommunicationError,
)
from app.application.ports.nebula_core_gateway import NebulaCoreGateway


router = APIRouter(
    prefix="/admin/monitor",
    tags=["Admin Monitor"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_core_error(error: Exception) -> None:
    if isinstance(error, CoreAuthenticationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error),
    ) from error


@router.get(
    "/summary",
    response_model=MonitorSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Monitor Summary (BFF)",
    description="Resumo de telemetria e logs para o Nebula Monitor.",
)
async def get_monitor_summary(
    hours: int = Query(default=24, ge=1, le=720),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> MonitorSummaryResponse:
    try:
        summary = await gateway.get_observability_summary(hours)
    except (CoreAuthenticationError, CoreCommunicationError) as error:
        _raise_core_error(error)

    return MonitorSummaryResponse(
        since=summary.since,
        total_events=summary.total_events,
        events_by_type=summary.events_by_type,
        events_per_hour=[
            MonitorHourlyPoint(hour=point.hour, count=point.count)
            for point in summary.events_per_hour
        ],
        total_logs=summary.total_logs,
        logs_by_level=summary.logs_by_level,
    )


@router.get(
    "/telemetry",
    response_model=MonitorTelemetryResponse,
    status_code=status.HTTP_200_OK,
    summary="Monitor Telemetry (BFF)",
)
async def list_telemetry(
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=500),
    device_id: str | None = None,
    event_type: str | None = None,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> MonitorTelemetryResponse:
    try:
        events = await gateway.list_telemetry_events(
            hours=hours,
            limit=limit,
            device_id=device_id,
            event_type=event_type,
        )
    except (CoreAuthenticationError, CoreCommunicationError) as error:
        _raise_core_error(error)

    return MonitorTelemetryResponse(
        events=[
            MonitorTelemetryEventOut(
                event_id=event.event_id,
                device_id=event.device_id,
                session_id=event.session_id,
                event_type=event.event_type,
                payload=event.payload,
                occurred_at=event.occurred_at,
            )
            for event in events
        ]
    )


@router.get(
    "/logs",
    response_model=MonitorLogsResponse,
    status_code=status.HTTP_200_OK,
    summary="Monitor Logs (BFF)",
)
async def list_logs(
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=500),
    device_id: str | None = None,
    level: str | None = None,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> MonitorLogsResponse:
    try:
        logs = await gateway.list_logs(
            hours=hours,
            limit=limit,
            device_id=device_id,
            level=level,
        )
    except (CoreAuthenticationError, CoreCommunicationError) as error:
        _raise_core_error(error)

    return MonitorLogsResponse(
        logs=[
            MonitorLogOut(
                log_id=log.log_id,
                device_id=log.device_id,
                session_id=log.session_id,
                level=log.level,
                message=log.message,
                occurred_at=log.occurred_at,
            )
            for log in logs
        ]
    )
