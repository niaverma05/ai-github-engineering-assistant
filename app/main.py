import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

from app.github import get_installation_access_token, get_pull_request_files

app = FastAPI(
    title="AI GitHub Engineering Assistant",
    version="0.1.0",
)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


@app.get("/health")
def health_check():
    return {"status": "ok"}


def verify_github_signature(
    payload_body: bytes,
    signature_header: str | None,
) -> bool:
    if not GITHUB_WEBHOOK_SECRET or not signature_header:
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(
        expected_signature,
        signature_header,
    )


@app.post("/webhooks/github")
async def github_webhook(request: Request):
    payload_body = await request.body()

    signature_header = request.headers.get("X-Hub-Signature-256")

    if not verify_github_signature(payload_body, signature_header):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub webhook signature",
        )

    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    print(f"Received GitHub event: {event_type}")

    if event_type == "pull_request":
        action = payload.get("action")

        if action in {"opened", "synchronize", "reopened"}:
            pull_request = payload["pull_request"]
            repository = payload["repository"]
            installation = payload["installation"]

            owner = repository["owner"]["login"]
            repository_name = repository["name"]
            pull_request_number = pull_request["number"]
            installation_id = installation["id"]

            print(f"Pull request action: {action}")
            print(f"Repository: {owner}/{repository_name}")
            print(f"Pull request number: {pull_request_number}")
            print(f"Pull request title: {pull_request['title']}")

            access_token = await get_installation_access_token(
                installation_id
            )

            changed_files = await get_pull_request_files(
                owner=owner,
                repository=repository_name,
                pull_request_number=pull_request_number,
                access_token=access_token,
            )

            print(f"Changed files: {len(changed_files)}")

            for file in changed_files:
                print("-" * 60)
                print(f"File: {file['filename']}")
                print(f"Status: {file['status']}")
                print(
                    f"Changes: +{file['additions']} "
                    f"-{file['deletions']}"
                )

                patch = file.get("patch")

                if patch:
                    print("Patch:")
                    print(patch)
                else:
                    print("Patch unavailable.")

    return {"status": "received"}