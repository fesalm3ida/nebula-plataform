from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress
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

    def delete(self, device_id: UUID) -> None:
        model = self._database_session.get(DeviceModel, device_id)

        if model is not None:
            self._database_session.delete(model)
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
        mac_address: MacAddress,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.mac_address == mac_address.value
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def find_by_fingerprint(
        self,
        fingerprint: DeviceFingerprint,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.fingerprint == fingerprint.value
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def find_by_device_key(
        self,
        device_key: DeviceKey,
    ) -> Device | None:
        statement = select(DeviceModel).where(
            DeviceModel.device_key == device_key.value
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return DeviceMapper.to_domain(model)

    def exists_by_fingerprint(
        self,
        fingerprint: DeviceFingerprint,
    ) -> bool:
        statement = select(DeviceModel.device_id).where(
            DeviceModel.fingerprint == fingerprint.value
        )

        device_id = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        return device_id is not None

    def find_all(self) -> list[Device]:
        statement = select(DeviceModel).order_by(
            DeviceModel.created_at
        )

        models = self._database_session.execute(
            statement
        ).scalars().all()

        return [DeviceMapper.to_domain(model) for model in models]
