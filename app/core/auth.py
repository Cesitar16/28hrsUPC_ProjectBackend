from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

import jwt
from fastapi import Depends, HTTPException, Request
from jwt import PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse

from app.core.settings import Settings

logger = logging.getLogger("midiarioia.auth")


@dataclass
class AuthenticatedUser:
    user_id: str
    email: Optional[str]
    token: str
    claims: dict[str, Any]


class TokenVerifier:
    """Verifies Supabase JWT tokens using JWKS."""

    def __init__(self, settings: Settings):
        jwks_url = settings.jwt_jwks_url or f"{str(settings.supabase_url).rstrip('/')}/auth/v1/jwks"
        self.jwks_client = PyJWKClient(jwks_url)
        self.audience = settings.jwt_audience
        self.issuer = settings.jwt_issuer

    def verify(self, token: str) -> AuthenticatedUser:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            options = {"verify_aud": bool(self.audience)}
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options=options,
            )
        except jwt.ExpiredSignatureError as exc:  # type: ignore[attr-defined]
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "unauthorized", "message": "Token expirado."}},
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "unauthorized", "message": "Token inválido."}},
            ) from exc

        user_id = decoded.get("sub") or decoded.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "unauthorized", "message": "Token sin identificador de usuario."}},
            )

        return AuthenticatedUser(
            user_id=str(user_id),
            email=decoded.get("email"),
            token=token,
            claims=decoded,
        )


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that verifies bearer tokens and stores the authenticated user."""

    def __init__(self, app, verifier: TokenVerifier):  # type: ignore[override]
        super().__init__(app)
        self.verifier = verifier

    async def dispatch(self, request: StarletteRequest, call_next):  # type: ignore[override]
        authorization = request.headers.get("Authorization")
        request.state.user = None

        if authorization:
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                return JSONResponse(
                    status_code=401,
                    content={"error": {"code": "unauthorized", "message": "Cabecera Authorization inválida."}},
                )
            try:
                user = self.verifier.verify(token)
                request.state.user = user
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content=exc.detail)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Unexpected error verifying token")
                return JSONResponse(
                    status_code=500,
                    content={"error": {"code": "internal_error", "message": "Error verificando token."}},
                )
        return await call_next(request)


def get_token_verifier(settings: Settings) -> TokenVerifier:
    return TokenVerifier(settings)


def get_current_user(request: Request) -> AuthenticatedUser:
    user: Optional[AuthenticatedUser] = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "Autenticación requerida."}},
        )
    return user


def get_optional_user(request: Request) -> Optional[AuthenticatedUser]:
    return getattr(request.state, "user", None)


def get_current_token(user: AuthenticatedUser = Depends(get_current_user)) -> str:
    return user.token
