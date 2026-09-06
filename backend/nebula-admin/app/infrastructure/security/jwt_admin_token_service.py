from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from app.application.security.admin_token_service import (
    AdminPrincipal,
    AdminToken,
    AdminTokenService,
)
from app.domain.enums.admin_role import AdminRole


class JWTAdminTokenService(AdminTokenService):
    TOKEN_TYPE = "access"
    BEARER_TOKEN_TYPE = "bearer"

    def __init__(
        self,
        secret_key: str,
        issuer: str,
        audience: str,
        algorithm: str = "HS256",
        expiration_minutes: int = 60,
    ) -> None:
        if not secret_key:
            raise ValueError("Admin JWT secret key cannot be empty.")

        if not issuer:
            raise ValueError("Admin JWT issuer cannot be empty.")

        if not audience:
            raise ValueError("Admin JWT audience cannot be empty.")

        if not algorithm:
            raise ValueError("Admin JWT algorithm cannot be empty.")

        if expiration_minutes <= 0:
            raise ValueError(
                "Admin JWT expiration must be greater than zero."
            )

        self._secret_key = secret_key
        self._issuer = issuer
        self._audience = audience
        self._algorithm = algorithm
        self._expiration_minutes = expiration_minutes

    def create_admin_access_token(
        self,
        admin_id: UUID,
        role: AdminRole,
    ) -> AdminToken:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(
            minutes=self._expiration_minutes
        )

        payload = {
            "iss": self._issuer,
            "sub": f"admin:{admin_id}",
            "aud": self._audience,
            "iat": issued_at,
            "nbf": issued_at,
            "exp": expires_at,
            "jti": str(uuid4()),
            "admin_id": str(admin_id),
            "role": role.value,
            "token_type": self.TOKEN_TYPE,
        }

        encoded_token = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

        return AdminToken(
            value=encoded_token,
            token_type=self.BEARER_TOKEN_TYPE,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def validate_admin_access_token(
        self,
        token: str,
    ) -> AdminPrincipal:
        if not token:
            raise ValueError("Invalid admin access token.")

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
                        "admin_id",
                        "role",
                        "token_type",
                    ],
                },
            )

            if payload["token_type"] != self.TOKEN_TYPE:
                raise ValueError("Invalid admin access token type.")

            admin_id = UUID(payload["admin_id"])
            role = AdminRole(payload["role"])

            if payload["sub"] != f"admin:{admin_id}":
                raise ValueError(
                    "Admin token subject does not match Admin."
                )

            return AdminPrincipal(admin_id=admin_id, role=role)

        except (
            jwt.PyJWTError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError("Invalid admin access token.") from error
