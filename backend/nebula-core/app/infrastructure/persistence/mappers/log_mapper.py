from app.domain.entities.log import Log
from app.domain.enums.log_level import LogLevel
from app.infrastructure.persistence.models.log_model import LogModel


class LogMapper:
    @staticmethod
    def to_model(log: Log) -> LogModel:
        return LogModel(
            log_id=log.log_id,
            session_id=log.session_id,
            device_id=log.device_id,
            level=log.level.value,
            message=log.message,
            occurred_at=log.occurred_at,
            received_at=log.received_at,
        )

    @staticmethod
    def to_domain(model: LogModel) -> Log:
        return Log(
            session_id=model.session_id,
            device_id=model.device_id,
            level=LogLevel(model.level),
            message=model.message,
            log_id=model.log_id,
            occurred_at=model.occurred_at,
            received_at=model.received_at,
        )
