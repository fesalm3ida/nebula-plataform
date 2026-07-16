from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AccessToken:
    value: str
    token_type: str
    issued_at: datetime
    expires_at: datetime


class AccessTokenService(ABC):
    @abstractmethod
    def create_device_access_token(
        self,
        device_id: UUID,
    ) -> AccessToken:
        """Create an access token for an authenticated Device."""

    @abstractmethod
    def validate_device_access_token(
        self,
        token: str,
    ) -> UUID:
        """
        Validate a Device access token.

        Return the authenticated Device identifier when valid.
        """
