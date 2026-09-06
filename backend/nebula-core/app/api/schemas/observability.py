from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.log_level import LogLevel
from app.domain.enums.telemetry_event_type import TelemetryEventType


class TelemetryEventRequest(BaseModel):
    session_id: UUID
    event_type: TelemetryEventType
    payload: dict[str, Any]
    occurred_at: datetime | None = None


class TelemetryEventResponse(BaseModel):
    event_id: UUID
    session_id: UUID
    device_id: UUID
    event_type: TelemetryEventType
    occurred_at: datetime
    received_at: datetime


class LogRequest(BaseModel):
    session_id: UUID
    level: LogLevel
    message: str = Field(min_length=1)
    occurred_at: datetime | None = None


class LogResponse(BaseModel):
    log_id: UUID
    session_id: UUID
    device_id: UUID
    level: LogLevel
    occurred_at: datetime
    received_at: datetime
