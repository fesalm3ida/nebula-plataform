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


class DeviceAlreadyBlockedError(Exception):
    """Raised when an already blocked Device is blocked again."""


class DeviceAlreadyRevokedError(Exception):
    """Raised when an already revoked Device is revoked again."""


class DeviceAlreadyExpiredError(Exception):
    """Raised when an already expired Device is expired again."""


class LicenseExpiredError(Exception):
    """Raised when a Device license (trial or annual) has expired."""


class PaymentGatewayError(Exception):
    """Raised when the payment provider cannot be reached or rejects it."""


class ActiveSessionAlreadyExistsError(Exception):
    """Raised when a Device already has an active Session."""


class SessionNotFoundError(Exception):
    """Raised when the requested Session does not exist."""


class SessionAlreadyClosedError(Exception):
    """Raised when a Session is no longer active."""


class SessionNotActiveError(Exception):
    """Raised when an operation requires an active Session."""


class SessionOwnershipError(Exception):
    """Raised when a Session does not belong to the authenticated Device."""


class PlaylistNotFoundError(Exception):
    """Raised when the requested Playlist does not exist."""


class PlaylistNotAvailableError(Exception):
    """Raised when a Playlist is not available for provisioning."""


class NoPlaylistAssignedError(Exception):
    """Raised when a Device has no active Playlist assigned."""


class PlaylistAssignmentAlreadyExistsError(Exception):
    """Raised when a Device already has an active PlaylistAssignment."""


class DeviceHasPaymentsError(Exception):
    """O Device possui pagamentos registrados e nao pode ser excluido.

    Pagamentos sao registro financeiro: para encerrar o acesso use
    revogar/bloquear em vez de apagar o aparelho.
    """
