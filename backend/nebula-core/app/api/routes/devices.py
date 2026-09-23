from collections.abc import Callable
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from app.api.dependencies.device_repository import get_device_repository
from app.api.dependencies.payment_repository import get_payment_repository
from app.api.schemas.device_activation import DeviceActivationResponse
from app.api.schemas.device_registration import (
    DeviceRegistrationRequest,
    DeviceRegistrationResponse,
)
from app.api.schemas.device_summary import (
    DeviceListResponse,
    DeviceSummaryResponse,
)
from app.api.security.admin import require_admin
from app.application.exceptions import (
    DeviceHasPaymentsError,
    DeviceAlreadyActiveError,
    DeviceAlreadyBlockedError,
    DeviceAlreadyExpiredError,
    DeviceAlreadyRegisteredError,
    DeviceAlreadyRevokedError,
    DeviceNotFoundError,
)
from app.application.use_cases.activate_device import (
    ActivateDeviceCommand,
    ActivateDeviceUseCase,
)
from app.application.use_cases.block_device import (
    BlockDeviceCommand,
    BlockDeviceUseCase,
)
from app.application.use_cases.delete_device import (
    DeleteDeviceCommand,
    DeleteDeviceUseCase,
)
from app.application.use_cases.reset_device_license import (
    ResetDeviceLicenseCommand,
    ResetDeviceLicenseUseCase,
)
from app.application.use_cases.expire_device import (
    ExpireDeviceCommand,
    ExpireDeviceUseCase,
)
from app.application.use_cases.list_devices import ListDevicesUseCase
from app.application.use_cases.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceUseCase,
)
from app.application.use_cases.revoke_device import (
    RevokeDeviceCommand,
    RevokeDeviceUseCase,
)
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.payment_repository import PaymentRepository


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post(
    "/register",
    response_model=DeviceRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Device",
)
def register_device(
    payload: DeviceRegistrationRequest,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceRegistrationResponse:
    use_case = RegisterDeviceUseCase(repository)

    command = RegisterDeviceCommand(
        fingerprint=payload.fingerprint,
        mac_address=payload.mac_address,
        platform=payload.platform,
        app_version=payload.app_version,
    )

    try:
        result = use_case.execute(command)

    except DeviceAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return DeviceRegistrationResponse(
        device_id=result.device_id,
        device_key=result.device_key,
        activation_code=result.activation_code,
        mac_address=result.mac_address,
        status=result.status,
    )


@router.get(
    "",
    response_model=DeviceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Devices",
    description=(
        "Administrative operation. Returns registered Devices "
        "(without sensitive identity fields). "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def list_devices(
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceListResponse:
    result = ListDevicesUseCase(repository).execute()

    return DeviceListResponse(
        devices=[
            DeviceSummaryResponse(
                device_id=device.device_id,
                platform=device.platform,
                status=device.status,
                app_version=device.app_version,
                created_at=device.created_at,
                mac_address=str(device.mac_address),
                activation_code=(
                    str(device.activation_code)
                    if device.activation_code is not None
                    else None
                ),
            )
            for device in result.devices
        ]
    )


@router.post(
    "/{device_id}/activate",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Device",
    description=(
        "Administrative operation. Moves a Device from Pending to Active. "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def activate_device(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    result = _lifecycle(
        execute=lambda: ActivateDeviceUseCase(repository).execute(
            ActivateDeviceCommand(device_id=device_id)
        ),
        not_found=DeviceNotFoundError,
        conflict=DeviceAlreadyActiveError,
    )

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )


@router.post(
    "/{device_id}/block",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Block Device",
    description=(
        "Administrative operation. Blocks a Device. "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def block_device(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    result = _lifecycle(
        execute=lambda: BlockDeviceUseCase(repository).execute(
            BlockDeviceCommand(device_id=device_id)
        ),
        not_found=DeviceNotFoundError,
        conflict=DeviceAlreadyBlockedError,
    )

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )


@router.post(
    "/{device_id}/revoke",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke Device",
    description=(
        "Administrative operation. Revokes a Device. "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def revoke_device(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    result = _lifecycle(
        execute=lambda: RevokeDeviceUseCase(repository).execute(
            RevokeDeviceCommand(device_id=device_id)
        ),
        not_found=DeviceNotFoundError,
        conflict=DeviceAlreadyRevokedError,
    )

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Device",
    description=(
        "Administrative operation. Removes a Device from the registry "
        "(sessions, playlist assignments and telemetry cascade). A Device "
        "with registered payments cannot be deleted - revoke or block it "
        "instead. Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def delete_device(
    device_id: UUID,
    device_repository: DeviceRepository = Depends(get_device_repository),
    payment_repository: PaymentRepository = Depends(
        get_payment_repository
    ),
) -> Response:
    _lifecycle(
        execute=lambda: DeleteDeviceUseCase(
            device_repository=device_repository,
            payment_repository=payment_repository,
        ).execute(DeleteDeviceCommand(device_id=device_id)),
        not_found=DeviceNotFoundError,
        conflict=DeviceHasPaymentsError,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{device_id}/reset-license",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Device License",
    description=(
        "Administrative operation. Removes the license and returns the "
        "Device to 'pending' (useful for support and tests). "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def reset_device_license(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    result = _lifecycle(
        execute=lambda: ResetDeviceLicenseUseCase(repository).execute(
            ResetDeviceLicenseCommand(device_id=device_id)
        ),
        not_found=DeviceNotFoundError,
        conflict=DeviceNotFoundError,
    )

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )


@router.post(
    "/{device_id}/expire",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Expire Device",
    description=(
        "Administrative operation. Expires a Device. "
        "Protected by the administration guard (X-Admin-Token)."
    ),
    dependencies=[Depends(require_admin)],
)
def expire_device(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    result = _lifecycle(
        execute=lambda: ExpireDeviceUseCase(repository).execute(
            ExpireDeviceCommand(device_id=device_id)
        ),
        not_found=DeviceNotFoundError,
        conflict=DeviceAlreadyExpiredError,
    )

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )


def _lifecycle(
    *,
    execute: Callable[[], Any],
    not_found: type[Exception],
    conflict: type[Exception],
) -> Any:
    try:
        return execute()
    except not_found as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except conflict as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
