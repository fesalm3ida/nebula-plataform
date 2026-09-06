from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.enums.telemetry_event_type import TelemetryEventType
from app.infrastructure.persistence.models.telemetry_event_model import (
    TelemetryEventModel,
)


class TelemetryEventMapper:
    @staticmethod
    def to_model(event: TelemetryEvent) -> TelemetryEventModel:
        return TelemetryEventModel(
            event_id=event.event_id,
            session_id=event.session_id,
            device_id=event.device_id,
            event_type=event.event_type.value,
            payload=event.payload,
            occurred_at=event.occurred_at,
            received_at=event.received_at,
        )

    @staticmethod
    def to_domain(model: TelemetryEventModel) -> TelemetryEvent:
        return TelemetryEvent(
            session_id=model.session_id,
            device_id=model.device_id,
            event_type=TelemetryEventType(model.event_type),
            payload=model.payload,
            event_id=model.event_id,
            occurred_at=model.occurred_at,
            received_at=model.received_at,
        )
