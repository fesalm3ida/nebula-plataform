class AuthenticationRequiredError(Exception):
    """Raised when Bearer credentials are missing."""


class InvalidAccessTokenError(Exception):
    """Raised when an access token cannot be validated."""


class AuthorizationDeniedError(Exception):
    """Raised when an authenticated identity lacks permission."""
