from typing import List

from pydantic import BaseModel, Field


class Issue(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    labels: List[str] = []
    due_at: int
    status: str = "open"


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    labels: List[str] = []
    due_at: int
    status: str = "open"
