"""Security hardening: startup secret validation, login rate limiting,
password policy, account-deletion password confirmation, and the
short-lived access token / refresh token flow."""

import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _register(client, email, password, full_name="Test User"):
    return client.post("/api/auth/register", json={
        "email": email, "password": password, "full_name": full_name,
    })


# ---------------------------------------------------------------- SECRET_KEY

def test_startup_fails_with_placeholder_secret_outside_dev():
    env = {**os.environ, "ENVIRONMENT": "production"}
    env.pop("SECRET_KEY", None)  # falls back to the .env placeholder
    res = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True,
    )
    assert res.returncode != 0, "placeholder SECRET_KEY must refuse to start in production"
    assert "SECRET_KEY" in (res.stderr or "")


def test_startup_passes_with_strong_secret_outside_dev():
    env = {**os.environ, "ENVIRONMENT": "production",
           "SECRET_KEY": "Xk9$2vQ7mLp0wR4tYb6nH1sD8fG3jA5cZ7eU2iO6p"}
    res = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True,
    )
    assert res.returncode == 0, res.stderr


def test_placeholder_secret_allowed_in_dev():
    env = {**os.environ, "ENVIRONMENT": "development"}
    env.pop("SECRET_KEY", None)
    res = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True,
    )
    assert res.returncode == 0, res.stderr


# ------------------------------------------------------------ password policy

def test_short_password_registration_rejected(client):
    res = _register(client, "weak.password@dualwell.edu", "short12345")  # 10 chars < 12
    assert res.status_code == 422


def test_minimum_length_password_accepted(client):
    res = _register(client, "edge.password@dualwell.edu", "123456789012")  # exactly 12
    assert res.status_code == 201


def test_long_password_registration_accepted(client):
    res = _register(client, "strong.password@dualwell.edu", "Correct-Horse-9")
    assert res.status_code == 201


# ---------------------------------------------------------------- rate limit

def test_login_rate_limiting_blocks_after_repeated_failures(client):
    email = "brute.force@dualwell.edu"
    res = _register(client, email, "BruteForce1234!", "Brute Force")
    assert res.status_code == 201

    for _ in range(5):
        res = client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})
        assert res.status_code == 401

    # 6th attempt is throttled before the password is even checked...
    res = client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})
    assert res.status_code == 429
    assert "retry-after" in res.headers

    # ...including when the password is actually correct.
    res = client.post("/api/auth/login", json={"email": email, "password": "BruteForce1234!"})
    assert res.status_code == 429


def test_other_accounts_unaffected_by_rate_limit(client):
    # While one account is locked, a different email on the same client
    # still logs in (the per-IP cap is far looser than the per-email cap).
    for _ in range(5):
        client.post("/api/auth/login",
                    json={"email": "locked.user@dualwell.edu", "password": "wrong"})

    res = _register(client, "unrelated.user@dualwell.edu", "UnrelatedUser123!",
                    "Unrelated User")
    assert res.status_code == 201
    assert "refresh_token" in res.json()


# --------------------------------------------------------- refresh-token flow

def test_login_returns_short_lived_access_and_refresh_tokens(client):
    email = "tokens.user@dualwell.edu"
    _register(client, email, "TokenUser12345!")
    login = client.post("/api/auth/login", json={"email": email, "password": "TokenUser12345!"})
    assert login.status_code == 200
    data = login.json()
    assert data["token_type"] == "bearer"
    assert data["refresh_token"]
    assert data["expires_in"] <= 15 * 60  # access token is short-lived, not 7 days


def test_refresh_returns_working_access_token(client):
    email = "refresh.user@dualwell.edu"
    _register(client, email, "RefreshUser1234!")
    login = client.post("/api/auth/login", json={"email": email, "password": "RefreshUser1234!"})
    refresh = login.json()["refresh_token"]

    refreshed = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert refreshed.status_code == 200
    new_access = refreshed.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_refresh_token_rejected_as_access_token(client):
    email = "sneaky.user@dualwell.edu"
    _register(client, email, "SneakyUser1234!")
    login = client.post("/api/auth/login", json={"email": email, "password": "SneakyUser1234!"})
    refresh = login.json()["refresh_token"]

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    assert res.status_code == 401


def test_refresh_rejects_garbage_token(client):
    res = client.post("/api/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert res.status_code == 401


def test_expired_access_token_rejected():
    import app.core.security as security
    expired = security._create_token(1, timedelta(seconds=-5), "access")
    assert security.decode_access_token(expired) is None


# ------------------------------------------------------ account deletion

def test_delete_account_requires_password(client, auth_headers):
    res = client.request("DELETE", "/api/privacy/delete-account", headers=auth_headers, json={})
    assert res.status_code == 422  # password missing entirely


def test_delete_account_rejects_wrong_password(client, auth_headers):
    res = client.request("DELETE", "/api/privacy/delete-account", headers=auth_headers,
                         json={"password": "totally-wrong"})
    assert res.status_code == 403
    # Account still exists afterwards.
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 200


def test_delete_account_with_correct_password(client):
    email = "eraseme@dualwell.edu"
    _register(client, email, "EraseMe123456!", "Erase Me")
    login = client.post("/api/auth/login", json={"email": email, "password": "EraseMe123456!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    res = client.request("DELETE", "/api/privacy/delete-account", headers=headers,
                         json={"password": "EraseMe123456!"})
    assert res.status_code == 200
    assert "permanently erased" in res.json()["message"]

    # The session token no longer resolves to a user.
    assert client.get("/api/auth/me", headers=headers).status_code in (401, 404)