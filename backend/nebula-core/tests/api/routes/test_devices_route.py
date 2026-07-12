from fastapi.testclient import TestClient

from app.api.dependencies.device_repository import get_device_repository
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.main import app


client = TestClient(app)


def reset_repository() -> None:
    repository = get_device_repository()

    if isinstance(repository, InMemoryDeviceRepository):
        repository._devices.clear()


def valid_payload() -> dict[str, str]:
    return {
        "fingerprint": "a" * 64,
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "platform": "android_tv",
        "app_version": "0.1.0",
    }


def test_should_register_device_through_http() -> None:
    reset_repository()

    response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["device_id"]
    assert len(body["device_key"]) >= 32
    assert body["status"] == "pending"


def test_should_return_conflict_for_duplicate_device() -> None:
    reset_repository()

    client.post(
        "/devices/register",
        json=valid_payload(),
    )

    response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_should_reject_invalid_fingerprint_length() -> None:
    reset_repository()

    payload = valid_payload()
    payload["fingerprint"] = "invalid"

    response = client.post(
        "/devices/register",
        json=payload,
    )

    assert response.status_code == 422


def test_should_reject_invalid_domain_data() -> None:
    reset_repository()

    payload = valid_payload()
    payload["fingerprint"] = "g" * 64

    response = client.post(
        "/devices/register",
        json=payload,
    )

    assert response.status_code == 422

def test_should_activate_registered_device_through_http() -> None:
    reset_repository()

    registration_response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    device_id = registration_response.json()["device_id"]

    response = client.post(
        f"/devices/{device_id}/activate"
    )

    assert response.status_code == 200
    assert response.json()["device_id"] == device_id
    assert response.json()["status"] == "active"


def test_should_return_not_found_when_activating_unknown_device() -> None:
    from uuid import uuid4

    reset_repository()

    response = client.post(
        f"/devices/{uuid4()}/activate"
    )

    assert response.status_code == 404


def test_should_return_conflict_when_device_is_already_active() -> None:
    reset_repository()

    registration_response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    device_id = registration_response.json()["device_id"]

    client.post(f"/devices/{device_id}/activate")

    response = client.post(
        f"/devices/{device_id}/activate"
    )

    assert response.status_code == 409
