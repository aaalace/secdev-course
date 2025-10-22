import time
from collections import defaultdict
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.issue import Issue, IssueCreate

app = FastAPI(title="Issue Lite", version="0.1.0")

# Rate limiting storage
_RATE_LIMIT_STORAGE = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds


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


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": str(exc)}},
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    # Clean old requests outside the window
    _RATE_LIMIT_STORAGE[client_ip] = [
        req_time
        for req_time in _RATE_LIMIT_STORAGE[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check if rate limit exceeded
    if len(_RATE_LIMIT_STORAGE[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "error": {"code": "rate_limit_exceeded", "message": "Too many requests"}
            },
        )

    # Add current request
    _RATE_LIMIT_STORAGE[client_ip].append(current_time)

    response = await call_next(request)
    return response


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
    if issue_id <= 0:
        raise ApiError(
            code="invalid_id", message="Issue ID must be positive", status=400
        )
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
