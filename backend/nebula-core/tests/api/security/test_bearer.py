from fastapi.security import HTTPBearer

from app.api.security.bearer import bearer_scheme


def test_should_expose_http_bearer_scheme() -> None:
    assert isinstance(bearer_scheme, HTTPBearer)


def test_should_disable_automatic_bearer_errors() -> None:
    assert bearer_scheme.auto_error is False
