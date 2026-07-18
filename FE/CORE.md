# Frontend Core

`src/core` owns browser infrastructure. It must not import feature components or pages. Feature modules consume Core through stable functions and types.

## Responsibilities

| Capability                                | Location             |
| ----------------------------------------- | -------------------- |
| Validated runtime environment             | `core/config/env.ts` |
| Axios, CSRF, correlation and idempotency  | `core/api`           |
| Normalized `ApiError` contract            | `core/api/errors.ts` |
| Session bootstrap and route authorization | `core/auth`          |
| Query retry/cache policy                  | `core/query`         |
| Global render failure boundary            | `core/errors`        |
| Replaceable observability adapter         | `core/observability` |

## API rules

- Use `apiClient`; do not create feature-local Axios instances.
- Branch on `ApiError.code` or `ApiError.status`, never backend message text.
- Show `ApiError.requestId` in support-oriented error screens when useful.
- Pass `createIdempotencyKey()` for retryable create/payment mutations and retain that key for the logical operation.
- Never place credentials, sessions, CSRF tokens, or personal data in logs.

Example:

```ts
const key = createIdempotencyKey()

await apiClient.post('/orders', input, {
  headers: { 'Idempotency-Key': key },
})
```

Queries retry transient network and server failures at most twice. Client errors do not retry. Mutations never retry automatically because their business semantics may not be idempotent.

## Dependency direction

```text
app -> modules -> core/shared
                 core -X-> modules
```

If Core needs a feature type, move the truly generic contract into Core or invert the dependency through a callback/provider. Do not import the feature directly.

## Feature data flow

Feature pages must remain composition-only:

```text
API adapter -> React Query hook -> reusable form/component -> page
                         client-only state -> Zustand store
```

- API adapters own URLs and response unwrapping.
- Query hooks own query keys, caching, invalidation and mutations.
- Zustand stores are reserved for client-owned state such as auth, cart and persisted chat state.
- Backend-owned state must stay in React Query; do not copy API collections into Zustand.
- Pages must not declare duplicated query keys or backend domain option arrays.
- Select options and defaults for statuses/types come from `/api/v1/admin/metadata`.
- Storefront identity, navigation, announcement, footer and hero content come from the backend `site_settings` record.

## Internationalization

- Supported locale codes are `en`, `vi`, `ja` and `ko`.
- `i18next` detects the saved language first, then the browser language, with English fallback.
- Translation JSON is lazy-loaded from `src/locales/<locale>/<namespace>.json`; unused languages are separate build chunks.
- Keep translations separated by application area: `common`, `storefront`, `auth`, and `admin`. Components must read UI labels from their owning namespace instead of hardcoding display text.
- The i18n bootstrap synchronizes the active locale to the HTML `lang` attribute. Locale-aware CSS applies Be Vietnam Pro for Vietnamese, Noto Sans/Serif JP for Japanese, and Noto Sans/Serif KR for Korean.
- Only `common` loads during bootstrap. Feature namespaces and locale-specific font stylesheets load on demand; language options prefetch their font on hover or focus.
- Locale-sensitive queries keep their previous response visible while translated storefront data refreshes, avoiding a full-page loader during language changes.
- The API client sends the active locale through `Accept-Language` on every request.
- React Query keys include the active locale for localized storefront responses.
- The language switcher displays EN, VN, JP and KR while requests use the standards-compliant codes.
