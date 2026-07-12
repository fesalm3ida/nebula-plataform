class DeviceAlreadyRegisteredError(Exception):
    """Raised when a Device with the same identity is already registered."""
    

class DeviceNotFoundError(Exception):
    """Raised when the requested Device does not exist."""


class InvalidDeviceCredentialsError(Exception):
    """Raised when Device credentials do not match."""


class DeviceNotActiveError(Exception):
    """Raised when a Device is not allowed to authenticate."""
