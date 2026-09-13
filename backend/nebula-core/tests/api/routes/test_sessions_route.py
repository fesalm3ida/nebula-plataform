from datetime import datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.main import app


client = TestClient(app)


def parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def make_device(
    fingerprint: str = "a" * 64,
    mac_address: str = "AA:BB:CC:DD:EE:FF",
    active: bool = True,
) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint(fingerprint),
        mac_address=MacAddress(mac_address),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )

    if active:
        device.activate()

    return device


def authorization_headers(
    device: Device,
) -> dict[str, str]:
    return {
        "Authorization": (
            f"Bearer fake-jwt:{device.device_id}"
        ),
    }


def start_session_for_device(
    device: Device,
) -> dict:
    response = client.post(
        "/sessions",
        headers=authorization_headers(device),
    )

    assert response.status_code == 201

    return response.json()


def test_should_start_session_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/sessions",
        headers=authorization_headers(device),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["session_id"]
    assert body["device_id"] == str(device.device_id)
    assert body["status"] == "active"
    assert body["started_at"]
    assert body["expires_at"]
    assert body["last_seen"]
    assert body["last_seen"] == body["started_at"]


def test_should_reject_missing_bearer_token() -> None:
    response = client.post("/sessions")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_invalid_bearer_token() -> None:
    response = client.post(
        "/sessions",
        headers={
            "Authorization": "Bearer invalid-access-token",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_token_for_unknown_device() -> None:
    response = client.post(
        "/sessions",
        headers={
            "Authorization": f"Bearer fake-jwt:{uuid4()}",
        },
    )

    assert response.status_code == 401


def test_should_reject_pending_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device(active=False)
    device_repository.save(device)

    response = client.post(
        "/sessions",
        headers=authorization_headers(device),
    )

    assert response.status_code == 403


def test_should_resume_active_session_on_second_start(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    headers = authorization_headers(device)

    first_response = client.post(
        "/sessions",
        headers=headers,
    )

    second_response = client.post(
        "/sessions",
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert (
        second_response.json()["session_id"]
        == first_response.json()["session_id"]
    )


def test_should_ignore_submitted_device_id(
    device_repository: InMemoryDeviceRepository,
) -> None:
    authenticated_device = make_device()
    device_repository.save(authenticated_device)

    another_device_id = uuid4()

    response = client.post(
        "/sessions",
        headers=authorization_headers(
            authenticated_device
        ),
        json={
            "device_id": str(another_device_id),
        },
    )

    assert response.status_code == 201
    assert response.json()["device_id"] == str(
        authenticated_device.device_id
    )
    assert response.json()["device_id"] != str(
        another_device_id
    )


def test_should_update_session_presence_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    original_last_seen = parse_api_datetime(
        session_body["last_seen"]
    )

    response = client.post(
        f"/sessions/{session_id}/heartbeat",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    updated_last_seen = parse_api_datetime(
        body["last_seen"]
    )

    assert body["session_id"] == session_id
    assert body["status"] == "active"
    assert updated_last_seen >= original_last_seen


def test_should_reject_heartbeat_without_bearer_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/heartbeat"
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_heartbeat_with_invalid_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/heartbeat",
        headers={
            "Authorization": "Bearer invalid-access-token",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_return_not_found_for_unknown_heartbeat_session(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        f"/sessions/{uuid4()}/heartbeat",
        headers=authorization_headers(device),
    )

    assert response.status_code == 404


def test_should_reject_heartbeat_for_session_owned_by_another_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    owner_device = make_device()

    authenticated_device = make_device(
        fingerprint="b" * 64,
        mac_address="11:22:33:44:55:66",
    )

    device_repository.save(owner_device)
    device_repository.save(authenticated_device)

    session_body = start_session_for_device(
        owner_device
    )
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/heartbeat",
        headers=authorization_headers(
            authenticated_device
        ),
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"]


def test_should_reject_heartbeat_for_ended_session(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]
    headers = authorization_headers(device)

    end_response = client.post(
        f"/sessions/{session_id}/end",
        headers=headers,
    )

    assert end_response.status_code == 200

    response = client.post(
        f"/sessions/{session_id}/heartbeat",
        headers=headers,
    )

    assert response.status_code == 409
    assert "ended" in response.json()["detail"]


def test_should_reject_heartbeat_for_expired_session(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    session = session_repository.find_by_id(
        UUID(session_id)
    )

    assert session is not None

    session.expire()
    session_repository.save(session)

    response = client.post(
        f"/sessions/{session_id}/heartbeat",
        headers=authorization_headers(device),
    )

    assert response.status_code == 409
    assert "expired" in response.json()["detail"]


def test_should_end_active_session_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/end",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["session_id"] == session_id
    assert body["status"] == "ended"
    assert body["ended_at"]


def test_should_reject_end_session_without_bearer_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/end"
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_end_session_with_invalid_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/end",
        headers={
            "Authorization": "Bearer invalid-access-token",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_return_not_found_when_ending_unknown_session(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        f"/sessions/{uuid4()}/end",
        headers=authorization_headers(device),
    )

    assert response.status_code == 404


def test_should_reject_end_session_owned_by_another_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    owner_device = make_device()

    authenticated_device = make_device(
        fingerprint="b" * 64,
        mac_address="11:22:33:44:55:66",
    )

    device_repository.save(owner_device)
    device_repository.save(authenticated_device)

    session_body = start_session_for_device(
        owner_device
    )
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/end",
        headers=authorization_headers(
            authenticated_device
        ),
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"]


def test_should_return_conflict_when_session_is_already_ended(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]
    headers = authorization_headers(device)

    first_response = client.post(
        f"/sessions/{session_id}/end",
        headers=headers,
    )

    second_response = client.post(
        f"/sessions/{session_id}/end",
        headers=headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409



