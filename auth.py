"""Hellō OpenID Connect login and tenant membership resolution."""

import logging
import os
from dataclasses import dataclass
from functools import cache

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import Connection, text

from db import get_connection

HELLO_ISSUER = "https://issuer.hello.coop"
HELLO_DISCOVERY_URL = f"{HELLO_ISSUER}/.well-known/openid-configuration"
LOCAL_DEVELOPMENT_ISSUER = "urn:contractor-readiness:local-development"
LOCAL_DEVELOPMENT_SUBJECT = "local-demo-manager"
oauth = OAuth()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Identity:
    issuer: str
    subject: str


@dataclass(frozen=True)
class Principal:
    issuer: str
    subject: str
    organisation_id: str
    role: str


@cache
def hello_client(client_id: str):
    return oauth.register(
        name="hello",
        client_id=client_id,
        server_metadata_url=HELLO_DISCOVERY_URL,
        client_kwargs={
            "scope": "openid",
            "token_endpoint_auth_method": "none",
            "code_challenge_method": "S256",
        },
    )


def get_hello_client():
    client_id = os.environ.get("HELLO_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=503, detail="Hellō login is not configured")
    return hello_client(client_id)


def get_authenticated_identity(request: Request) -> Identity:
    issuer = request.session.get("oidc_issuer")
    subject = request.session.get("oidc_subject")
    if not isinstance(issuer, str) or not isinstance(subject, str) or not subject:
        raise HTTPException(
            status_code=401,
            detail="Sign in is required",
            headers={"WWW-Authenticate": "Session"},
        )
    return Identity(issuer=issuer, subject=subject)


def get_session_identity(identity: Identity = Depends(get_authenticated_identity)) -> dict:
    return {"issuer": identity.issuer, "subject": identity.subject}


def get_current_principal(
    identity: Identity = Depends(get_authenticated_identity),
    connection: Connection = Depends(get_connection),
    requested_organisation: str | None = Header(default=None, alias="X-Organisation-ID"),
) -> Principal:
    if (
        os.environ.get("APP_ENV", "development").lower() == "development"
        and identity.issuer == LOCAL_DEVELOPMENT_ISSUER
        and identity.subject == LOCAL_DEVELOPMENT_SUBJECT
    ):
        return Principal(
            LOCAL_DEVELOPMENT_ISSUER,
            LOCAL_DEVELOPMENT_SUBJECT,
            "ORG-DEMO",
            "manager",
        )

    membership_query = """
        SELECT organisation_id, role
        FROM user_organisation_memberships
        WHERE issuer = :issuer AND subject = :subject AND active = TRUE
    """
    parameters = {"issuer": identity.issuer, "subject": identity.subject}
    if requested_organisation is not None:
        membership_query += " AND organisation_id = :organisation_id"
        parameters["organisation_id"] = requested_organisation
    memberships = connection.execute(
        text(membership_query + " ORDER BY organisation_id"), parameters
    ).mappings().all()

    if not memberships:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "No active organisation membership",
                "issuer": identity.issuer,
                "subject": identity.subject,
            },
        )
    if requested_organisation is None and len(memberships) != 1:
        raise HTTPException(
            status_code=400,
            detail="Select an organisation with the X-Organisation-ID header",
        )

    membership = memberships[0]
    return Principal(
        identity.issuer,
        identity.subject,
        membership["organisation_id"],
        membership["role"],
    )


def require_manager(principal: Principal = Depends(get_current_principal)) -> Principal:
    if principal.role != "manager":
        raise HTTPException(status_code=403, detail="Manager permission required")
    return principal


async def begin_hello_login(request: Request):
    client = get_hello_client()
    redirect_uri = os.environ.get(
        "HELLO_REDIRECT_URI", "http://localhost:8000/auth/callback"
    )
    return await client.authorize_redirect(
        request,
        redirect_uri,
        response_type="code",
    )


async def complete_hello_login(request: Request):
    client = get_hello_client()
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as error:
        logger.warning(
            "Hellō token exchange failed (%s): %s; session_cookie_present=%s; pending_oauth_states=%s",
            getattr(error, "error", "unknown_error"),
            getattr(error, "description", "No provider description"),
            request.cookies.get("contractor_readiness_session") is not None,
            sum(key.startswith("_state_") for key in request.session),
        )
        raise HTTPException(status_code=401, detail="Hellō sign-in could not be verified") from error

    user_info = token.get("userinfo")
    if not user_info or user_info.get("iss") != HELLO_ISSUER:
        raise HTTPException(status_code=401, detail="Hellō returned an invalid identity")
    subject = user_info.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="Hellō returned no valid subject")

    request.session.clear()
    request.session["oidc_issuer"] = HELLO_ISSUER
    request.session["oidc_subject"] = subject
    return subject
