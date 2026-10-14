import os
import time

import httpx
import jwt

GITHUB_API_URL = "https://api.github.com"

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")


def generate_app_jwt() -> str:
    if not GITHUB_APP_ID:
        raise RuntimeError("GITHUB_APP_ID is not configured")

    if not GITHUB_PRIVATE_KEY_PATH:
        raise RuntimeError("GITHUB_PRIVATE_KEY_PATH is not configured")

    with open(GITHUB_PRIVATE_KEY_PATH, "r") as private_key_file:
        private_key = private_key_file.read()

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + (9 * 60),
        "iss": GITHUB_APP_ID,
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )

    return token


async def get_installation_access_token(installation_id: int) -> str:
    app_jwt = generate_app_jwt()

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = (
        f"{GITHUB_API_URL}/app/installations/"
        f"{installation_id}/access_tokens"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)

    response.raise_for_status()

    return response.json()["token"]


async def get_pull_request_files(
    owner: str,
    repository: str,
    pull_request_number: int,
    access_token: str,
) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = (
        f"{GITHUB_API_URL}/repos/{owner}/{repository}/"
        f"pulls/{pull_request_number}/files"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    response.raise_for_status()

    return response.json()