import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

app = FastAPI(
    title="AI GitHub Engineering Assistant",
    version="0.1.0",
)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


@app.get("/health")
def health_check():
    return {"status": "ok"}


def verify_github_signature(payload_body: bytes, signature_header: str | None) -> bool:
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

    return hmac.compare_digest(expected_signature, signature_header)


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
        pull_request = payload.get("pull_request", {})

        print(f"Pull request action: {action}")
        print(f"Pull request number: {pull_request.get('number')}")
        print(f"Pull request title: {pull_request.get('title')}")

    return {"status": "received"}