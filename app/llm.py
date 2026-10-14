import os

from google import genai

from app.review import PullRequestReview

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


async def review_pull_request(
    title: str,
    description: str,
    changed_files: list[dict],
) -> PullRequestReview:
    diff_sections = []

    for file in changed_files:
        patch = file.get("patch")

        if not patch:
            continue

        diff_sections.append(
            f"""
FILE: {file["filename"]}
STATUS: {file["status"]}
ADDITIONS: {file["additions"]}
DELETIONS: {file["deletions"]}

DIFF:
{patch}
"""
        )

    combined_diff = "\n".join(diff_sections)

    prompt = f"""
You are an expert software engineer performing a pull request code review.

Analyze the proposed code changes and identify meaningful problems.

Focus on:
- potential bugs
- security vulnerabilities
- code quality problems
- missing or insufficient tests
- performance problems

Only report issues that are supported by the provided pull request diff.
Do not invent problems simply to produce findings.

For every finding:
- identify the relevant file
- classify the issue
- assign an appropriate severity
- explain why the issue matters
- provide a concrete suggestion for improving it

If the changes appear correct, it is acceptable to return no findings.

PULL REQUEST TITLE:
{title}

PULL REQUEST DESCRIPTION:
{description}

CHANGED FILES:

{combined_diff}
"""

    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PullRequestReview,
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return PullRequestReview.model_validate_json(response.text)