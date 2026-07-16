from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from app.application.security.access_token_service import (
    AccessToken,
    AccessTokenService,
)


class JWTAccessTokenService(AccessTokenService):
    TOKEN_TYPE = "access"
    BEARER_TOKEN_TYPE = "bearer"

    def __init__(
        self,
        secret_key: str,
        issuer: str,
        audience: str,
        algorithm: str = "HS256",
        expiration_minutes: int = 30,
    ) -> None:
        if not secret_key:
            raise ValueError("JWT secret key cannot be empty.")

        if not issuer:
            raise ValueError("JWT issuer cannot be empty.")

        if not audience:
            raise ValueError("JWT audience cannot be empty.")

        if not algorithm:
            raise ValueError("JWT algorithm cannot be empty.")

        if expiration_minutes <= 0:
            raise ValueError(
                "JWT expiration must be greater than zero."
            )

        self._secret_key = secret_key
        self._issuer = issuer
        self._audience = audience
        self._algorithm = algorithm
        self._expiration_minutes = expiration_minutes

    def create_device_access_token(
        self,
        device_id: UUID,
    ) -> AccessToken:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(
            minutes=self._expiration_minutes
        )

        payload = {
            "iss": self._issuer,
            "sub": f"device:{device_id}",
            "aud": self._audience,
            "iat": issued_at,
            "nbf": issued_at,
            "exp": expires_at,
            "jti": str(uuid4()),
            "device_id": str(device_id),
            "token_type": self.TOKEN_TYPE,
        }

        encoded_token = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

        return AccessToken(
            value=encoded_token,
            token_type=self.BEARER_TOKEN_TYPE,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def validate_device_access_token(
        self,
        token: str,
    ) -> UUID:
        if not token:
            raise ValueError("Invalid access token.")

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": [
                        "iss",
                        "sub",
                        "aud",
                        "iat",
                        "nbf",
                        "exp",
                        "jti",
                        "device_id",
                        "token_type",
                    ],
                },
            )

            if payload["token_type"] != self.TOKEN_TYPE:
                raise ValueError("Invalid access token type.")

            device_id = UUID(payload["device_id"])

            if payload["sub"] != f"device:{device_id}":
                raise ValueError(
                    "Access token subject does not match Device."
                )

            return device_id

        except (
            jwt.PyJWTError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError("Invalid access token.") from error
