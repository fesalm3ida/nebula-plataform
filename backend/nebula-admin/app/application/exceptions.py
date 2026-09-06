class InvalidCredentialsError(Exception):
    """Raised when administrative credentials are invalid."""


class CoreCommunicationError(Exception):
    """Raised when the Nebula Core cannot be reached or returns an error."""
