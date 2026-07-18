# Meridian Nexus

Meridian Nexus is a modular commerce platform connecting storefront, customer accounts, administration, promotions, content, orders, and real-time customer support.

## Technology

| Area     | Stack                                               | Location             |
| -------- | --------------------------------------------------- | -------------------- |
| Backend  | FastAPI, SQLAlchemy, Argon2id, server-side sessions | `BE/`                |
| Frontend | React 19, TypeScript, Vite, TanStack Query          | `FE/`                |
| Delivery | GitHub Actions, Docker, GHCR                        | `.github/workflows/` |

The application follows a modular-monolith structure. Business capabilities own their API, data access, schemas, hooks, stores, and UI while shared infrastructure remains in dedicated core packages.

## Local development

1. Copy `BE/.env.example` to `BE/.env` and replace `APP_KEY` with a random secret.
2. Copy `FE/.env.example` to `FE/.env`.
3. Follow `BE/README.md` and `FE/README.md` to start each application.
4. Open `http://localhost:5173`; the API is available at `http://127.0.0.1:8000`.

Never commit real `.env` files, credentials, access tokens, database files, or production customer data.

## Delivery workflow

- `prod`: production-ready code only.
- `staging`: QA and demonstration releases.
- `dev`: integration branch for completed features.
- `feat/<name>`: feature work created from `dev`.
- `hotfix/<name>`: urgent production fixes created from `prod`.

All changes enter protected branches through pull requests. See `CONTRIBUTING.md` and `docs/GITFLOW.md` for the complete workflow and commit convention.

## Quality

```bash
cd BE
ruff format --check northstar tests_python scripts
ruff check northstar tests_python scripts
pytest
pip-audit -r requirements.txt

cd ../FE
npm ci
npm run quality
npm audit --audit-level=high
```

No application can be guaranteed to be unhackable. Production operation still requires TLS, managed secrets, MFA, backups, monitoring, a reverse proxy or WAF, and regular dependency/security review.
