import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse

from app.main import app

_RATE_LIMIT_STORAGE = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60


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
