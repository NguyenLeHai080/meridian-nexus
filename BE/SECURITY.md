# Security Baseline

- Argon2id password hashing with automatic migration from legacy bcrypt hashes.
- Opaque session tokens; only SHA-256 token digests are stored in the database.
- `HttpOnly`, `SameSite=Lax`, optionally `Secure` authentication cookies.
- Strict Origin validation and double-submit CSRF protection on every state-changing request.
- Trusted host enforcement, CORS allow-listing, request IDs, security headers, and no-store responses.
- Role and permission checks on every administration endpoint.
- Per-IP and per-account authentication throttling plus security event auditing.
- Transactional stock updates and request-bound idempotency for checkout.
- Strict request schemas with unknown fields rejected and stable non-leaking error responses.
- One MiB request-body limit to reduce parser and memory-exhaustion attacks.
- Constant-cost password verification for unknown accounts to reduce timing-based enumeration.
- Production startup validation for HTTPS origins, HSTS, `Secure` cookies, and `__Host-` cookie names.
- Production image excludes test, lint, audit, and multipart packages.
- Non-root container runtime and a persistent database volume with least-privilege ownership.

Production deployments must terminate TLS at a trusted reverse proxy, use a secret manager, rotate `APP_KEY` through a planned session invalidation, use Redis for distributed rate limits, centralize audit logs, enable MFA for privileged users, back up the database, and run dependency/image scanning in CI.
