from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.issue import Issue, IssueCreate

app = FastAPI(title="Issue Lite", version="0.1.0")


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


_DB = {"issues": []}
_ID_SEQ = 1


@app.post("/issues", response_model=Issue)
def create_issue(issue: IssueCreate):
    global _ID_SEQ
    new_issue = Issue(id=_ID_SEQ, **issue.model_dump())
    _DB["issues"].append(new_issue)
    _ID_SEQ += 1
    return new_issue


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: int):
    for issue in _DB["issues"]:
        if issue.id == issue_id:
            return issue
    raise ApiError(code="nf_error", message="Issue not found", status=404)


@app.put("/issues/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, data: IssueCreate):
    for i, issue in enumerate(_DB["issues"]):
        if issue.id == issue_id:
            updated = Issue(id=issue_id, **data.model_dump())
            _DB["issues"][i] = updated
            return updated
    raise ApiError(code="nf_error", message="Issue not found", status=404)


@app.delete("/issues/{issue_id}")
def delete_issue(issue_id: int):
    for i, issue in enumerate(_DB["issues"]):
        if issue.id == issue_id:
            del _DB["issues"][i]
            return {"message": "deleted"}
    raise ApiError(code="nf_error", message="Issue not found", status=404)


@app.get("/issues", response_model=List[Issue])
def list_issues(
    label: Optional[str] = Query(None), status: Optional[str] = Query(None)
):
    results = _DB["issues"]
    if label:
        results = [i for i in results if label in i.labels]
    if status:
        results = [i for i in results if i.status == status]
    return results
