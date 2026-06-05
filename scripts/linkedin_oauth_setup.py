#!/usr/bin/env python3
"""Interactive helper to complete LinkedIn OAuth and print env values.

Usage:
  ./scripts/linkedin_oauth_setup.py
  ./scripts/linkedin_oauth_setup.py --env-file .env.stg --write-env
  ./scripts/linkedin_oauth_setup.py --smoke-test-only
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import urllib.parse
import webbrowser
from datetime import date
from pathlib import Path

import requests


AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POSTS_URL = "https://api.linkedin.com/rest/posts"


def load_env_file(path: Path) -> None:
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        if not key or not key.replace("_", "").isalnum():
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LinkedIn OAuth setup helper")
    parser.add_argument("--env-file", default=".env", help="Path to env file (default: .env)")
    parser.add_argument("--no-open", action="store_true", help="Do not auto-open browser")
    parser.add_argument(
        "--scopes",
        default=os.environ.get("LI_SCOPES", "w_member_social openid profile"),
        help='OAuth scopes as space-separated string (default: "w_member_social openid profile")',
    )
    parser.add_argument("--state", default=f"duckiehunt-{secrets.token_hex(8)}", help="OAuth state value")
    parser.add_argument("--callback-url", help="Optional full callback URL")
    parser.add_argument("--auth-code", help="Optional auth code")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a LinkedIn post smoke test after OAuth/token steps",
    )
    parser.add_argument(
        "--smoke-test-only",
        action="store_true",
        help="Skip OAuth; use existing env vars to run only LinkedIn smoke test",
    )
    parser.add_argument(
        "--commentary",
        default="Duckiehunt LinkedIn integration test",
        help="Commentary text for the smoke-test post",
    )
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Update env file with LI_ACCESS_TOKEN, LI_PERSON_URN, LI_API_VERSION",
    )
    return parser.parse_args()


def require_env(var: str) -> str:
    value = os.environ.get(var, "").strip()
    if not value:
        raise SystemExit(f"Missing required env var: {var}")
    return value


def build_auth_url(client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def extract_code(callback_url: str) -> str:
    parsed = urllib.parse.urlparse(callback_url)
    query = urllib.parse.parse_qs(parsed.query)
    codes = query.get("code", [])
    return codes[0] if codes else ""


def is_nonexistent_version_payload(data: object) -> bool:
    if not isinstance(data, dict):
        return False
    return data.get("code") == "NONEXISTENT_VERSION"


def is_missing_version_payload(data: object) -> bool:
    if not isinstance(data, dict):
        return False
    return data.get("code") == "VERSION_MISSING"


def discover_api_version(access_token: str) -> str:
    year = date.today().year
    month = date.today().month
    for _ in range(36):
        candidate = f"{year}{month:02d}"
        response = requests.post(
            POSTS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "LinkedIn-Version": candidate,
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json={},
            timeout=20,
        )
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not is_nonexistent_version_payload(data):
            return candidate
        month -= 1
        if month == 0:
            year -= 1
            month = 12
    raise SystemExit("Could not discover an active LinkedIn-Version. Check app/token permissions.")


def exchange_code_for_token(
    code: str, client_id: str, client_secret: str, redirect_uri: str
) -> dict:
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
        raise SystemExit(f"Token exchange failed ({response.status_code}): {json.dumps(data)}")
    return data


def fetch_sub(access_token: str, api_version: str) -> str:
    if not api_version:
        api_version = discover_api_version(access_token)
        os.environ["LI_API_VERSION"] = api_version
    headers = {"Authorization": f"Bearer {access_token}"}
    if api_version:
        headers["LinkedIn-Version"] = api_version
    response = requests.get(
        USERINFO_URL,
        headers=headers,
        timeout=30,
    )
    if response.status_code == 426:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if is_nonexistent_version_payload(data):
            fallback_version = discover_api_version(access_token)
            os.environ["LI_API_VERSION"] = fallback_version
            response = requests.get(
                USERINFO_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "LinkedIn-Version": fallback_version,
                },
                timeout=30,
            )
    if not response.ok:
        # Return empty and let caller decide if they want manual URN.
        return ""
    data = response.json()
    return data.get("sub", "")


def upsert_env_values(path: Path, updates: dict[str, str]) -> None:
    lines = path.read_text().splitlines()
    keys = set(updates)
    found: set[str] = set()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        replaced = False
        for key, value in updates.items():
            if stripped.startswith(f"{key}="):
                out.append(f"{key}={value}")
                found.add(key)
                replaced = True
                break
        if not replaced:
            out.append(line)
    for key in keys - found:
        out.append(f"{key}={updates[key]}")
    path.write_text("\n".join(out) + "\n")


def resolve_author_urn() -> str:
    return (
        os.environ.get("LI_AUTHOR_URN", "").strip()
        or os.environ.get("LI_PERSON_URN", "").strip()
        or os.environ.get("LI_ORGANIZATION_URN", "").strip()
    )


def run_smoke_test(access_token: str, author_urn: str, api_version: str, commentary: str) -> dict:
    if not api_version:
        api_version = discover_api_version(access_token)
        os.environ["LI_API_VERSION"] = api_version
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if api_version:
        headers["LinkedIn-Version"] = api_version
    response = requests.post(
        POSTS_URL,
        headers=headers,
        json={
            "author": author_urn,
            "commentary": commentary,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        },
        timeout=30,
    )
    if response.status_code in (400, 426):
        try:
            body = response.json()
        except ValueError:
            body = {}
        if is_nonexistent_version_payload(body) or is_missing_version_payload(body):
            fallback_version = discover_api_version(access_token)
            os.environ["LI_API_VERSION"] = fallback_version
            headers["LinkedIn-Version"] = fallback_version
            response = requests.post(
                POSTS_URL,
                headers=headers,
                json={
                    "author": author_urn,
                    "commentary": commentary,
                    "visibility": "PUBLIC",
                    "distribution": {
                        "feedDistribution": "MAIN_FEED",
                        "targetEntities": [],
                        "thirdPartyDistributionChannels": [],
                    },
                    "lifecycleState": "PUBLISHED",
                    "isReshareDisabledByAuthor": False,
                },
                timeout=30,
            )
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}
    if not response.ok:
        raise SystemExit(
            f"Smoke test post failed ({response.status_code}): {json.dumps(body)}"
        )
    post_id = body.get("id") if isinstance(body, dict) else None
    if not post_id:
        post_id = response.headers.get("x-restli-id")
    return {"post_id": post_id, "response": body}


def main() -> int:
    args = parse_args()
    env_file = Path(args.env_file)
    if not env_file.exists():
        raise SystemExit(f"Env file not found: {env_file}")

    load_env_file(env_file)

    api_version = os.environ.get("LI_API_VERSION", "").strip()

    if args.smoke_test_only:
        access_token = require_env("LI_ACCESS_TOKEN")
        author_urn = resolve_author_urn()
        if not author_urn:
            raise SystemExit("Missing LI_AUTHOR_URN/LI_PERSON_URN/LI_ORGANIZATION_URN for smoke test")
        result = run_smoke_test(access_token, author_urn, api_version, args.commentary)
        print(f"Smoke test posted successfully. post_id={result['post_id']}")
        return 0

    client_id = require_env("LI_CLIENT_ID")
    client_secret = require_env("LI_CLIENT_SECRET")
    redirect_uri = require_env("LI_REDIRECT_URI")

    auth_url = build_auth_url(client_id, redirect_uri, args.scopes, args.state)
    print("\nOpen this URL and approve access:\n")
    print(auth_url)
    print("")

    if not args.no_open:
        webbrowser.open(auth_url)

    code = args.auth_code or ""
    if not code and args.callback_url:
        code = extract_code(args.callback_url)
    if not code:
        callback_url = input("Paste full callback URL (or just auth code): ").strip()
        code = extract_code(callback_url) if "://" in callback_url else callback_url
    if not code:
        raise SystemExit("No auth code found.")

    token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    access_token = token_data["access_token"]
    sub = fetch_sub(access_token, api_version)

    person_urn = f"urn:li:person:{sub}" if sub else ""

    print("\nSet these env values:\n")
    print(f"LI_ACCESS_TOKEN={access_token}")
    if person_urn:
        print(f"LI_PERSON_URN={person_urn}")
    else:
        print("# Could not auto-fetch LI_PERSON_URN (userinfo scope/product may be missing).")
    if api_version:
        print(f"LI_API_VERSION={api_version}")
    else:
        print("# LI_API_VERSION not set (using LinkedIn default API version)")
    print("")

    if args.write_env:
        updates = {
            "LI_ACCESS_TOKEN": access_token,
        }
        final_api_version = os.environ.get("LI_API_VERSION", "").strip()
        if final_api_version:
            updates["LI_API_VERSION"] = final_api_version
        if person_urn:
            updates["LI_PERSON_URN"] = person_urn
        upsert_env_values(env_file, updates)
        print(f"Updated {env_file} with LinkedIn values.")

    if args.smoke_test:
        author_urn = os.environ.get("LI_AUTHOR_URN", "").strip() or person_urn or os.environ.get("LI_PERSON_URN", "").strip() or os.environ.get("LI_ORGANIZATION_URN", "").strip()
        if not author_urn:
            raise SystemExit("Cannot run smoke test: missing LI_AUTHOR_URN/LI_PERSON_URN/LI_ORGANIZATION_URN")
        result = run_smoke_test(access_token, author_urn, api_version, args.commentary)
        print(f"Smoke test posted successfully. post_id={result['post_id']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
