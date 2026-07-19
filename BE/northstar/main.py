import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from northstar.core.bootstrap import bootstrap_reference_data
from northstar.core.config import get_settings
from northstar.core.database import engine, initialize_database
from northstar.core.http import (
    ApiError,
    RequestSizeLimitMiddleware,
    SecurityMiddleware,
    install_exception_handlers,
    limiter,
    success,
)
from northstar.modules.admin.router import router as admin_router
from northstar.modules.auth.router import csrf_router
from northstar.modules.auth.router import router as auth_router
from northstar.modules.chat.router import router as chat_router
from northstar.modules.customer.router import router as customer_router
from northstar.modules.storefront.router import router as storefront_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    bootstrap_reference_data()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=settings.max_request_bytes)
app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Idempotency-Key",
        "X-Request-ID",
        "X-XSRF-TOKEN",
    ],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
install_exception_handlers(app)
app.include_router(csrf_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(storefront_router)
app.include_router(chat_router)
app.include_router(customer_router)


if settings.app_env == "local":

    @app.get("/docs", include_in_schema=False)
    def swagger_docs(request: Request) -> HTMLResponse:
        nonce = secrets.token_urlsafe(24)
        request.state.csp_nonce = nonce
        response = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
        )
        html = response.body.decode("utf-8").replace("<script>", f'<script nonce="{nonce}">', 1)
        return HTMLResponse(html)


@app.get("/health/live")
def liveness(request: Request):
    return success(request, {"status": "ok"})


@app.get("/health")
@app.get("/health/ready")
def readiness(request: Request):
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception as error:
        raise ApiError("Database is unavailable.", "DATABASE_UNAVAILABLE", 503) from error
    if not limiter.is_healthy():
        raise ApiError("Rate limiter is unavailable.", "RATE_LIMIT_UNAVAILABLE", 503)
    return success(request, {"status": "ok"})
