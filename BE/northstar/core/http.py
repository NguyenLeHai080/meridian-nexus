import logging
import re
import secrets
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import UTC, datetime
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from northstar.core.config import get_settings
from northstar.core.network import client_ip

logger = logging.getLogger("northstar.api")

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{7,63}$")


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        *,
        errors: dict[str, list[str]] | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.errors = errors or {}
        self.details = details or {}


def success(
    request: Request,
    data: object,
    message: str = "Success.",
    status_code: int = 200,
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "data": data,
        "message": message,
        "request_id": request.state.request_id,
    }
    if meta is not None:
        payload["meta"] = meta
    return JSONResponse(payload, status_code=status_code)


def pagination_meta(page: int, per_page: int, total: int) -> dict[str, object]:
    last_page = max(1, (total + per_page - 1) // per_page)
    start = None
    end = None
    if total > 0:
        start = ((page - 1) * per_page) + 1
        end = min(page * per_page, total)
    return {
        "pagination": {
            "current_page": page,
            "from": start,
            "last_page": last_page,
            "per_page": per_page,
            "to": end,
            "total": total,
        }
    }


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._hits = 0

    def hit(self, key: str, limit: int, seconds: int) -> None:
        now = datetime.now(UTC).timestamp()
        threshold = now - seconds
        with self._lock:
            self._hits += 1
            if self._hits % 1024 == 0:
                stale_keys = [
                    event_key
                    for event_key, event_values in self._events.items()
                    if not event_values or event_values[-1] <= threshold
                ]
                for stale_key in stale_keys:
                    self._events.pop(stale_key, None)
            events = self._events[key]
            while events and events[0] <= threshold:
                events.popleft()
            if len(events) >= limit:
                raise ApiError("Too many requests.", "RATE_LIMITED", 429)
            events.append(now)

    def is_healthy(self) -> bool:
        return True


class RedisSlidingWindowLimiter:
    _SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local threshold = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])
local member = ARGV[5]
redis.call('ZREMRANGEBYSCORE', key, '-inf', threshold)
local count = redis.call('ZCARD', key)
if count >= limit then
    redis.call('PEXPIRE', key, ttl)
    return 0
end
redis.call('ZADD', key, now, member)
redis.call('PEXPIRE', key, ttl)
return 1
"""

    def __init__(self, url: str, *, fail_closed: bool) -> None:
        self._redis = Redis.from_url(url, decode_responses=True)
        self._fail_closed = fail_closed
        self._fallback = SlidingWindowLimiter()

    def hit(self, key: str, limit: int, seconds: int) -> None:
        now_ms = int(datetime.now(UTC).timestamp() * 1000)
        try:
            allowed = self._redis.eval(
                self._SCRIPT,
                1,
                f"northstar:rate-limit:{key}",
                now_ms,
                now_ms - (seconds * 1000),
                limit,
                seconds * 1000,
                f"{now_ms}:{secrets.token_hex(8)}",
            )
        except RedisError as error:
            if self._fail_closed:
                logger.error("Redis rate limiter unavailable", exc_info=error)
                raise ApiError(
                    "Service temporarily unavailable.", "RATE_LIMIT_UNAVAILABLE", 503
                ) from error
            self._fallback.hit(key, limit, seconds)
            return
        if int(allowed) != 1:
            raise ApiError("Too many requests.", "RATE_LIMITED", 429)

    def is_healthy(self) -> bool:
        try:
            return bool(self._redis.ping())
        except RedisError:
            return False


def build_rate_limiter() -> SlidingWindowLimiter | RedisSlidingWindowLimiter:
    settings = get_settings()
    if settings.redis_url:
        return RedisSlidingWindowLimiter(
            settings.redis_url,
            fail_closed=settings.app_env.lower() == "production",
        )
    return SlidingWindowLimiter()


limiter = build_rate_limiter()


class RequestTooLargeError(Exception):
    """Raised before request parsing when the configured body limit is exceeded."""


class RequestSizeLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                if int(content_length) > self.max_bytes:
                    await self._reject(scope, receive, send)
                    return
            except ValueError:
                await self._reject(scope, receive, send)
                return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise RequestTooLargeError
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestTooLargeError:
            await self._reject(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        state = scope.get("state", {})
        response = JSONResponse(
            {
                "data": None,
                "message": "Request body is too large.",
                "error": {"code": "REQUEST_TOO_LARGE", "details": {}},
                "request_id": state.get("request_id"),
            },
            status_code=413,
        )
        await response(scope, receive, send)


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        settings = get_settings()
        supplied_request_id = request.headers.get("X-Request-ID", "")
        request_id = supplied_request_id
        if REQUEST_ID_PATTERN.fullmatch(supplied_request_id) is None:
            request_id = secrets.token_hex(16)
        request.state.request_id = request_id

        request_client_ip = client_ip(request)
        try:
            limiter.hit(f"api:{request_client_ip}", settings.api_rate_limit, 60)
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                origin = request.headers.get("Origin")
                if origin not in settings.frontend_origins:
                    raise ApiError("Request origin is not allowed.", "UNTRUSTED_ORIGIN", 403)
                csrf_cookie = request.cookies.get("XSRF-TOKEN", "")
                csrf_header = request.headers.get("X-XSRF-TOKEN", "")
                if (
                    not csrf_cookie
                    or not csrf_header
                    or not secrets.compare_digest(csrf_cookie, csrf_header)
                ):
                    raise ApiError("CSRF token mismatch.", "CSRF_TOKEN_MISMATCH", 419)
            response = await call_next(request)
        except ApiError as error:
            response = error_response(request, error)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        csp_nonce = getattr(request.state, "csp_nonce", None)
        if csp_nonce is None:
            content_security_policy = settings.content_security_policy
        else:
            content_security_policy = (
                "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
                "form-action 'none'; connect-src 'self'; "
                f"script-src 'nonce-{csp_nonce}' https://cdn.jsdelivr.net; "
                "style-src https://cdn.jsdelivr.net; "
                "img-src https://fastapi.tiangolo.com data:"
            )
        response.headers["Content-Security-Policy"] = content_security_policy
        if settings.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age}; includeSubDomains; preload"
            )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


def error_response(request: Request, error: ApiError) -> JSONResponse:
    payload: dict[str, object] = {
        "data": None,
        "message": error.message,
        "error": {"code": error.code, "details": error.details},
        "request_id": getattr(request.state, "request_id", None),
    }
    if error.errors:
        payload["errors"] = error.errors
    return JSONResponse(payload, status_code=error.status_code)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, error: ApiError) -> JSONResponse:
        return error_response(request, error)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, error: RequestValidationError) -> JSONResponse:
        errors: dict[str, list[str]] = {}
        for item in error.errors():
            location = item.get("loc", ())
            field = ".".join(str(part) for part in location if part not in {"body", "query"})
            errors.setdefault(field or "request", []).append(str(item.get("msg", "Invalid value.")))
        return error_response(
            request,
            ApiError("The given data was invalid.", "VALIDATION_ERROR", 422, errors=errors),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled API error", exc_info=error)
        return JSONResponse(
            {
                "data": None,
                "message": "An unexpected server error occurred.",
                "error": {"code": "INTERNAL_ERROR", "details": {}},
                "request_id": getattr(request.state, "request_id", None),
            },
            status_code=500,
        )
