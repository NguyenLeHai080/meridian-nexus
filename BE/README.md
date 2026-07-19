# Northstar API

Production-oriented FastAPI backend for the Northstar commerce platform. The API keeps the existing `/api/v1` contract used by the React frontend.

## Architecture

- `northstar/core`: configuration, database lifecycle, HTTP contract, auth, security, serialization, and bootstrap data.
- `northstar/modules/auth`: registration, login, logout, session state, and CSRF cookie.
- `northstar/modules/storefront`: localized catalog, journal, and contact endpoints.
- `northstar/modules/customer`: profile, order history, transactional checkout, stock control, and idempotency.
- `northstar/modules/chat`: public customer conversations.
- `northstar/modules/admin`: RBAC-protected commerce administration.
- `migrations`: idempotent SQLite schema migrations.
- `tests_python`: contract and security tests.

## Run

```bash
docker build -t northstar-api .
docker run --name home-api --restart unless-stopped \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  -v home-api-data:/data \
  northstar-api
```

The API is available at `http://localhost:8000`; local OpenAPI documentation is available at `/docs`. Put a trusted HTTPS reverse proxy in front of the API when it must accept remote traffic; do not expose the application container directly.

## Quality

```bash
pip install -r requirements-dev.txt
ruff format --check northstar tests_python scripts
ruff check northstar tests_python scripts
pytest
pip-audit -r requirements.txt
python scripts/security_smoke.py --target http://127.0.0.1:8000
```

## Authentication

Authentication uses opaque, high-entropy server-side sessions in an `HttpOnly` cookie. Passwords use Argon2id. Legacy bcrypt hashes are accepted once and upgraded automatically after a successful login. State-changing requests require both a trusted `Origin` and a matching double-submit CSRF token.

Production authentication requires verified email, SMTP delivery, TOTP multi-factor authentication for privileged roles, one-time recovery codes, expiring password-reset tokens, and auditable session revocation. MFA secrets are encrypted with a key derived from `APP_KEY`; rotating that key requires a planned MFA re-enrollment procedure.

For production, start from `.env.production.example`. Startup fails closed unless PostgreSQL, Redis, HTTPS-only origins, `Secure` cookies, HSTS, trusted hosts, and the `__Host-` cookie prefix are configured. Redis-backed sliding-window limits are mandatory in production and PostgreSQL migrations are serialized with an advisory transaction lock.
