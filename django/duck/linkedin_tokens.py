"""LinkedIn OAuth helpers used by admin token management views."""
from __future__ import annotations

import urllib.parse

import requests


AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def build_linkedin_authorize_url(client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def linkedin_exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    data = response.json()
    if not response.ok or "access_token" not in data:
        raise ValueError(f"LinkedIn code exchange failed ({response.status_code})")
    return data


def linkedin_refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> dict:
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    data = response.json()
    if not response.ok or "access_token" not in data:
        raise ValueError(f"LinkedIn token refresh failed ({response.status_code})")
    return data


def linkedin_fetch_person_urn(access_token: str, api_version: str = "") -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    if api_version:
        headers["LinkedIn-Version"] = api_version
    response = requests.get(USERINFO_URL, headers=headers, timeout=30)
    if not response.ok:
        return ""
    data = response.json()
    sub = data.get("sub")
    if not sub:
        return ""
    return f"urn:li:person:{sub}"


def upsert_env_values(path, updates: dict[str, str]) -> None:
    lines = path.read_text().splitlines() if path.exists() else []
    found = set()
    output = []

    for line in lines:
        stripped = line.strip()
        replaced = False
        for key, value in updates.items():
            if stripped.startswith(f"{key}="):
                output.append(f"{key}={value}")
                found.add(key)
                replaced = True
                break
        if not replaced:
            output.append(line)

    for key, value in updates.items():
        if key not in found:
            output.append(f"{key}={value}")

    path.write_text("\n".join(output) + "\n")
