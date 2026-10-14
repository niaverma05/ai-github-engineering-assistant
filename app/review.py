from typing import Literal

from pydantic import BaseModel


class ReviewFinding(BaseModel):
    category: Literal[
        "bug",
        "security",
        "quality",
        "testing",
        "performance",
    ]
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    file: str
    description: str
    explanation: str
    suggestion: str


class PullRequestReview(BaseModel):
    summary: str
    findings: list[ReviewFinding]