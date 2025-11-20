import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger
from .request_id import request_id_ctx

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request_id_ctx.get() or getattr(request.state, "request_id", "unknown")
        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"Query: {request.query_params} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"[{request_id}] {response.status_code} "
                f"({process_time:.3f}s)"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] 500 Internal Server Error "
                f"({process_time:.3f}s) | Exception: {e}"
            )
            raise