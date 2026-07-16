from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.repositories.device_repository import DeviceRepository
from app.infrastructure.persistence.mappers.device_mapper import (
    DeviceMapper,
)
from app.infrastructure.persistence.models.device_model import (
    DeviceModel,
)


class PostgreSQLDeviceRepository(DeviceRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, device: Device) -> None:
        model = DeviceMapper.to_model(device)

        self._database_session.merge(model)
        self._database_session.commit()

    def find_by_id(
        self,
        device_id: UUID,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.device_id == device_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def find_by_mac_address(
        self,
        mac_address: str,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.mac_address == mac_address.upper()
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def find_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.fingerprint == fingerprint.lower()
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def find_by_device_key(
        self,
        device_key: str,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.device_key == device_key
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def exists_by_fingerprint(
        self,
        fingerprint: str,
    ) -> bool:
        statement = select(DeviceModel.device_id).where(
            DeviceModel.fingerprint == fingerprint.lower()
        )

        device_id = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        return device_id is not None
