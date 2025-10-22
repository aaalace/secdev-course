from typing import List

from pydantic import BaseModel, Field, field_validator


class Issue(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    labels: List[str] = []
    due_at: int
    status: str = "open"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["open", "closed", "in_progress"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v):
        if len(v) > 10:
            raise ValueError("maximum 10 labels allowed")
        return v


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    labels: List[str] = []
    due_at: int
    status: str = "open"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["open", "closed", "in_progress"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v):
        if len(v) > 10:
            raise ValueError("maximum 10 labels allowed")
        return v
