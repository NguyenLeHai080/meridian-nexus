# Frontend Web

React 19 + TypeScript frontend organized by business module. Application wiring is isolated from reusable core infrastructure and feature code.

Core dependency rules and API usage are documented in `CORE.md`.

## Local setup

```bash
cp .env.example .env
npm install
npm run dev
```

Quality checks:

```bash
npm run format
npm run quality
```

The individual checks remain available when diagnosing a failure:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

## Source layout

```text
src/
├── app/                  # Router and global providers
├── core/                 # API client, configuration, auth infrastructure
├── modules/              # Business features (API, hooks, schemas, UI, pages)
├── shared/               # Reusable presentation components and layouts
└── test/                 # Global test setup
```

Feature modules may depend on `core` and `shared`. `core` must not import feature UI. Other modules should consume a feature's public types or API rather than reaching into its internal components.

Authentication uses Sanctum's stateful SPA flow. The browser receives an encrypted `HttpOnly` session cookie, while Axios obtains and sends the CSRF token automatically. No access token is exposed to JavaScript or browser storage.

## Commerce routes

Public commerce pages live under `/`, `/about`, `/products`, `/contact` and `/journal`. Authenticated customers use `/checkout` and `/profile`. The permission-aware back office lives under `/admin` with separate product, order, promotion, content, user and conversation pages.

The storefront module owns public shopping UI and cart state. The admin module owns back-office API adapters and pages. Both consume stable commerce types, while authentication and HTTP/session concerns remain in `core`.

Chat currently uses short polling to preserve a small deployment footprint. Its conversation contract is ready to become the fallback transport when Laravel Reverb or another WebSocket gateway is introduced.
