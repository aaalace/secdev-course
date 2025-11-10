import time
from collections import defaultdict
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.issue import Issue, IssueCreate
from app.models import IssueModel

app = FastAPI(title="Issue Lite", version="0.1.0")


# Initialize database
@app.on_event("startup")
def startup():
    init_db()


# Rate limiting storage
_RATE_LIMIT_STORAGE = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60


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
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    _RATE_LIMIT_STORAGE[client_ip] = [
        req_time
        for req_time in _RATE_LIMIT_STORAGE[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    if len(_RATE_LIMIT_STORAGE[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "error": {"code": "rate_limit_exceeded", "message": "Too many requests"}
            },
        )

    _RATE_LIMIT_STORAGE[client_ip].append(current_time)

    response = await call_next(request)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/issues", response_model=Issue)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    new_issue = IssueModel(
        title=issue.title, labels=issue.labels, due_at=issue.due_at, status=issue.status
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return Issue(
        id=new_issue.id,
        title=new_issue.title,
        labels=new_issue.labels,
        due_at=new_issue.due_at,
        status=new_issue.status,
    )


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    if issue_id <= 0:
        raise ApiError(
            code="invalid_id", message="Issue ID must be positive", status=400
        )
    issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not issue:
        raise ApiError(code="nf_error", message="Issue not found", status=404)
    return Issue(
        id=issue.id,
        title=issue.title,
        labels=issue.labels,
        due_at=issue.due_at,
        status=issue.status,
    )


@app.put("/issues/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, data: IssueCreate, db: Session = Depends(get_db)):
    issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not issue:
        raise ApiError(code="nf_error", message="Issue not found", status=404)

    issue.title = data.title
    issue.labels = data.labels
    issue.due_at = data.due_at
    issue.status = data.status

    db.commit()
    db.refresh(issue)

    return Issue(
        id=issue.id,
        title=issue.title,
        labels=issue.labels,
        due_at=issue.due_at,
        status=issue.status,
    )


@app.delete("/issues/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not issue:
        raise ApiError(code="nf_error", message="Issue not found", status=404)

    db.delete(issue)
    db.commit()
    return {"message": "deleted"}


@app.get("/issues", response_model=List[Issue])
def list_issues(
    label: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(IssueModel)

    if search:
        query = query.filter(IssueModel.title.ilike(f"%{search}%"))
    if label:
        query = query.filter(IssueModel.labels.contains([label]))
    if status:
        query = query.filter(IssueModel.status == status)

    issues = query.all()
    return [
        Issue(id=i.id, title=i.title, labels=i.labels, due_at=i.due_at, status=i.status)
        for i in issues
    ]
