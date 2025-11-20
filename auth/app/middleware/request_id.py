import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_ctx.set(request_id)
        request.state.request_id = request_id  # доступен в endpoint через request.state.request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response