from uuid import UUID

from pydantic import BaseModel


class MonitorHourlyPoint(BaseModel):
    hour: str
    count: int


class MonitorSummaryResponse(BaseModel):
    since: str
    total_events: int
    events_by_type: dict[str, int]
    events_per_hour: list[MonitorHourlyPoint]
    total_logs: int
    logs_by_level: dict[str, int]


class MonitorTelemetryEventOut(BaseModel):
    event_id: UUID
    device_id: UUID
    session_id: UUID
    event_type: str
    payload: dict
    occurred_at: str


class MonitorTelemetryResponse(BaseModel):
    events: list[MonitorTelemetryEventOut]


class MonitorLogOut(BaseModel):
    log_id: UUID
    device_id: UUID
    session_id: UUID
    level: str
    message: str
    occurred_at: str


class MonitorLogsResponse(BaseModel):
    logs: list[MonitorLogOut]
