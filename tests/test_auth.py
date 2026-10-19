import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.testclient import TestClient

import auth
import api
from auth import LOCAL_DEVELOPMENT_ISSUER, LOCAL_DEVELOPMENT_SUBJECT
import api
from api import app
from auth import (
    LOCAL_DEVELOPMENT_ISSUER,
    LOCAL_DEVELOPMENT_SUBJECT,
    Identity,
    Principal,
    get_authenticated_identity,
    get_current_principal,
    require_manager,
)


def request_with_session(session: dict) -> Request:
    request = Request({
        "type": "http",
        "method": "GET",
        "scheme": "http",
        "path": "/auth/callback",
        "headers": [],
        "query_string": b"",
        "server": ("localhost", 8000),
        "client": ("127.0.0.1", 1234),
    })
    request.scope["session"] = session
    return request


def test_missing_session_is_rejected():
    with pytest.raises(HTTPException) as error:
        get_authenticated_identity(request_with_session({}))

    assert error.value.status_code == 401


def test_session_provides_verified_identity():
    identity = get_authenticated_identity(request_with_session({
        "oidc_issuer": "https://issuer.hello.coop",
        "oidc_subject": "hello-subject",
    }))

    assert identity == Identity("https://issuer.hello.coop", "hello-subject")


def test_membership_is_resolved_by_issuer_subject_and_selected_tenant():
    class Rows:
        def all(self):
            return [{"organisation_id": "ORG-DEMO", "role": "manager"}]

    class Result:
        def mappings(self):
            return Rows()

    class Connection:
        def execute(self, query, parameters):
            assert parameters == {
                "issuer": "https://issuer.hello.coop",
                "subject": "hello-subject",
                "organisation_id": "ORG-DEMO",
            }
            return Result()

    principal = get_current_principal(
        Identity("https://issuer.hello.coop", "hello-subject"),
        Connection(),
        "ORG-DEMO",
    )

    assert principal == Principal(
        "https://issuer.hello.coop", "hello-subject", "ORG-DEMO", "manager"
    )


def test_viewer_cannot_perform_manager_actions():
    viewer = Principal("https://issuer.hello.coop", "viewer", "ORG-DEMO", "viewer")

    with pytest.raises(HTTPException) as error:
        require_manager(viewer)

    assert error.value.status_code == 403


def test_manager_can_perform_manager_actions():
    manager = Principal("https://issuer.hello.coop", "manager", "ORG-DEMO", "manager")

    assert require_manager(manager) == manager


def test_local_demo_identity_gets_manager_access_only_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    principal = get_current_principal(
        Identity(LOCAL_DEVELOPMENT_ISSUER, LOCAL_DEVELOPMENT_SUBJECT), None, None
    )

    assert principal == Principal(
        LOCAL_DEVELOPMENT_ISSUER,
        LOCAL_DEVELOPMENT_SUBJECT,
        "ORG-DEMO",
        "manager",
    )


def test_local_demo_identity_does_not_bypass_membership_in_production(monkeypatch):
    class Rows:
        def all(self):
            return []

    class Result:
        def mappings(self):
            return Rows()

    class Connection:
        def execute(self, _query, _parameters):
            return Result()

    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(HTTPException) as error:
        get_current_principal(
            Identity(LOCAL_DEVELOPMENT_ISSUER, LOCAL_DEVELOPMENT_SUBJECT),
            Connection(),
            None,
        )

    assert error.value.status_code == 403


def test_local_demo_login_is_disabled_outside_development(monkeypatch):
    monkeypatch.setattr(api, "app_environment", "production")
    response = TestClient(app).post("/auth/dev-login")

    assert response.status_code == 404


def test_local_demo_login_sets_session_in_development(monkeypatch):
    monkeypatch.setattr(api, "app_environment", "development")
    with TestClient(app) as client:
        response = client.post("/auth/dev-login")
        identity_response = client.get("/auth/identity")

    assert response.status_code == 200
    assert identity_response.json() == {
        "issuer": LOCAL_DEVELOPMENT_ISSUER,
        "subject": LOCAL_DEVELOPMENT_SUBJECT,
    }


def test_local_demo_identity_gets_manager_access_only_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    principal = get_current_principal(
        Identity(LOCAL_DEVELOPMENT_ISSUER, LOCAL_DEVELOPMENT_SUBJECT),
        None,
        None,
    )

    assert principal == Principal(
        LOCAL_DEVELOPMENT_ISSUER,
        LOCAL_DEVELOPMENT_SUBJECT,
        "ORG-DEMO",
        "manager",
    )


def test_local_demo_identity_does_not_bypass_membership_in_production(monkeypatch):
    class Rows:
        def all(self):
            return []

    class Result:
        def mappings(self):
            return Rows()

    class Connection:
        def execute(self, _query, _parameters):
            return Result()

    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(HTTPException) as error:
        get_current_principal(
            Identity(LOCAL_DEVELOPMENT_ISSUER, LOCAL_DEVELOPMENT_SUBJECT),
            Connection(),
            None,
        )

    assert error.value.status_code == 403


def test_local_demo_login_is_disabled_outside_development(monkeypatch):
    monkeypatch.setattr(api, "app_environment", "production")

    response = TestClient(app).post("/auth/dev-login")

    assert response.status_code == 404


def test_local_demo_login_sets_session_in_development(monkeypatch):
    monkeypatch.setattr(api, "app_environment", "development")

    with TestClient(app) as client:
        response = client.post("/auth/dev-login")
        identity_response = client.get("/auth/identity")

    assert response.status_code == 200
    assert identity_response.json() == {
        "issuer": LOCAL_DEVELOPMENT_ISSUER,
        "subject": LOCAL_DEVELOPMENT_SUBJECT,
    }


def test_callback_stores_identity_only_and_discards_provider_tokens(monkeypatch):
    class Client:
        async def authorize_access_token(self, _request):
            return {
                "access_token": "provider-access-token",
                "id_token": "provider-id-token",
                "userinfo": {
                    "iss": "https://issuer.hello.coop",
                    "sub": "hello-subject",
                },
            }

    monkeypatch.setattr(auth, "get_hello_client", lambda: Client())
    request = request_with_session({"oauth_state": "temporary"})

    asyncio.run(auth.complete_hello_login(request))

    assert request.session == {
        "oidc_issuer": "https://issuer.hello.coop",
        "oidc_subject": "hello-subject",
    }


def test_login_session_cookie_round_trips_through_callback(monkeypatch):
    class Client:
        async def authorize_redirect(self, request, redirect_uri, response_type):
            request.session["test_oauth_state"] = "verified-state"
            return RedirectResponse("https://wallet.example/authorize")

        async def authorize_access_token(self, request):
            if request.session.get("test_oauth_state") != request.query_params.get("state"):
                raise AssertionError("OAuth session cookie was not returned")
            return {
                "userinfo": {
                    "iss": "https://issuer.hello.coop",
                    "sub": "hello-subject",
                }
            }

    monkeypatch.setattr(auth, "get_hello_client", lambda: Client())
    monkeypatch.setenv("HELLO_FRONTEND_URL", "http://127.0.0.1:5173/")

    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        login_response = client.get("/auth/login", follow_redirects=False)

        assert login_response.status_code == 307
        assert "contractor_readiness_session" in login_response.cookies

        callback_response = client.get(
            "/auth/callback?state=verified-state&code=authorization-code",
            follow_redirects=False,
        )

    assert callback_response.status_code == 307
