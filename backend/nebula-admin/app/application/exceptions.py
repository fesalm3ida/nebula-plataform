class InvalidCredentialsError(Exception):
    """Raised when administrative credentials are invalid."""


class CoreCommunicationError(Exception):
    """Raised when the Nebula Core cannot be reached or returns an error."""


class CoreResourceNotFoundError(Exception):
    """Raised when the Nebula Core reports a resource as not found."""


class CoreConflictError(Exception):
    """Raised when the Nebula Core rejects an operation for state reasons."""
