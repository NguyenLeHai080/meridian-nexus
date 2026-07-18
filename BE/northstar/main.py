from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from northstar.core.bootstrap import bootstrap_reference_data
from northstar.core.config import get_settings
from northstar.core.database import initialize_database
from northstar.core.http import (
    RequestSizeLimitMiddleware,
    SecurityMiddleware,
    install_exception_handlers,
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
    docs_url="/docs" if settings.app_env == "local" else None,
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


@app.get("/health")
def health(request: Request):
    return success(request, {"status": "ok"})
