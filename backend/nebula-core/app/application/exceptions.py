class DeviceAlreadyRegisteredError(Exception):
    """Raised when a Device with the same identity is already registered."""


class DeviceNotFoundError(Exception):
    """Raised when the requested Device does not exist."""


class InvalidDeviceCredentialsError(Exception):
    """Raised when Device credentials do not match."""


class DeviceNotActiveError(Exception):
    """Raised when a Device is not allowed to perform an operation."""


class DeviceAlreadyActiveError(Exception):
    """Raised when an already active Device is activated again."""


class ActiveSessionAlreadyExistsError(Exception):
    """Raised when a Device already has an active Session."""


class SessionNotFoundError(Exception):
    """Raised when the requested Session does not exist."""


class SessionAlreadyClosedError(Exception):
    """Raised when a Session is no longer active."""


class SessionNotActiveError(Exception):
    """Raised when an operation requires an active Session."""



