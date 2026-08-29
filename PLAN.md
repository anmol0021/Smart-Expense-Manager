# Smart Expense & Budget Manager - Implementation Plan

**Source specification:** [SPEC.md](SPEC.md)
**Planning status:** MVP implementation complete locally; deployment verification pending
**Scope:** Version 1 MVP

## 1. Specification Review

`SPEC.md` is suitable as the implementation source of truth. It covers the MVP goals, user stories, security rules, data model, API surface, financial calculations, testing strategy, deployment expectations, and viva documentation.

No requirement changes are needed before implementation. The following decisions make intentionally open details concrete for the MVP:

- **Backend:** FastAPI, Python, Pydantic, SQLAlchemy, and Alembic.
- **Database:** PostgreSQL. SQLite may be used only for isolated unit tests if PostgreSQL is unavailable, provided behavior remains equivalent.
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, and Recharts.
- **Authentication:** Secure HTTP-only cookie-based session. Passwords use Argon2id hashing. The server owns session validation and logout invalidation.
- **Money:** PostgreSQL `NUMERIC(12, 2)` and Python `Decimal`; amounts must be positive and limited to two decimal places.
- **Currency:** INR for the MVP, displayed consistently as `₹`. Currency conversion is out of scope.
- **Dates:** Transaction dates cannot be in the future. Timestamps are stored in UTC; the application timezone is configurable through an environment variable and defaults to `Asia/Kolkata`.
- **Ownership errors:** Return `404` for resources outside the authenticated user's scope, avoiding resource-existence disclosure.
- **Category ownership:** Seeded categories are global and immutable by ordinary users in the MVP. Custom categories remain optional and are deferred until the core workflow is stable.
- **Budget uniqueness:** Enforce `UNIQUE(user_id, category_id, month)` at the database level.
- **Alerts:** Implement budget status in dashboard responses first. Persisted duplicate-resistant alert records are optional after the core budget workflow passes its tests.

## 2. Delivery Principles

1. Implement one vertical slice at a time.
2. Keep all financial calculations in backend services.
3. Enforce authentication and ownership in the backend, never only in the UI.
4. Add migrations and tests with each persisted feature.
5. Keep API responses and errors consistent with `SPEC.md`.
6. Update README and `VIVA.md` as architecture decisions become final.
7. Do not add optional features until the MVP checklist is complete.

## 3. Target Repository Structure

```text
frontend/
  app/
  components/
  hooks/
  services/
  tests/
backend/
  app/
    api/
    core/
    models/
    repositories/
    schemas/
    services/
  tests/
  alembic/
.env.example
.gitignore
README.md
VIVA.md
SPEC.md
PLAN.md
```

## 4. Data Model

### Users

- `id UUID PRIMARY KEY`
- `name`
- `email` normalized to lowercase, unique and not null
- `password_hash` not null
- `created_at`, `updated_at`

### Categories

- `id UUID PRIMARY KEY`
- `name`
- `type` constrained to `INCOME` or `EXPENSE`
- `is_active`
- `created_at`, `updated_at`

Seed the predefined income and expense categories from `SPEC.md` through a repeatable migration or seed script.

### Transactions

- `id UUID PRIMARY KEY`
- `user_id` foreign key to users
- `category_id` foreign key to categories
- `type` constrained to `INCOME` or `EXPENSE`
- `amount NUMERIC(12, 2)`
- nullable `description` with maximum length 255
- `transaction_date DATE`
- `created_at`, `updated_at`

Validate that the transaction type matches the category type. Add indexes for user, date, category, and common user/date queries.

### Budgets

- `id UUID PRIMARY KEY`
- `user_id` foreign key to users
- `category_id` foreign key to categories
- `month` represented as the first day of the month or a validated `YYYY-MM` value at the API boundary
- `amount NUMERIC(12, 2)` and greater than zero
- `created_at`, `updated_at`
- unique constraint on `user_id`, `category_id`, and `month`

Budgets accept only expense categories.

### Sessions

Use a server-side session table or equivalent secure session store containing a token hash, user id, expiry, created timestamp, and revocation timestamp. Never persist raw session tokens.

## 5. Implementation Phases

### Phase 0 - Project Setup

- Initialize frontend and backend projects.
- Configure TypeScript, Python formatting/linting, environment loading, and `.gitignore`.
- Add `.env.example` with `DATABASE_URL`, `SECRET_KEY`, `SESSION_COOKIE_NAME`, `CORS_ORIGINS`, and `APP_TIMEZONE`.
- Add health endpoint `GET /health`.
- Add a minimal CI command set for linting, type checking, and tests.

**Exit checks:** both applications start locally, health check responds, no secrets are tracked.

### Phase 1 - Database and Seed Data

- Create SQLAlchemy models and Alembic migrations.
- Add foreign keys, check constraints, uniqueness constraints, and indexes.
- Seed all predefined categories.
- Add database integration tests for relationships, constraints, duplicate budgets, and category-type validation.

**Exit checks:** a fresh database can migrate and seed deterministically.

### Phase 2 - Authentication

- Implement registration with email normalization and password policy validation.
- Hash passwords with Argon2id.
- Implement login, secure HTTP-only cookie creation, session lookup, and logout revocation.
- Add authentication dependency/middleware for protected routes.
- Return safe user representations that never contain passwords or session secrets.
- Add tests for registration, duplicate email, invalid credentials, logout, expired/revoked sessions, and protected endpoints.

**Exit checks:** unauthenticated requests are rejected and authenticated identity is available to services.

### Phase 3 - Transaction Vertical Slice

- Implement create, list, detail, update, and delete transaction APIs.
- Validate amount, type, category, description, and non-future date.
- Add filtering by date range, type, and category.
- Add case-insensitive description search.
- Add sorting and bounded pagination with a maximum page size of 100.
- Enforce ownership in every repository query and service operation.
- Build the transaction form and history UI with accessible labels and validation messages.

**Exit checks:** a user can complete the full transaction workflow and cannot access another user's records.

### Phase 4 - Budget Vertical Slice

- Implement budget CRUD APIs for expense categories.
- Enforce positive amounts and one budget per user/category/month.
- Implement spent, remaining, utilization, and threshold classification using `Decimal`.
- Add budget status UI with normal, warning, critical, and exceeded states.
- Add tests for all boundaries: 0%, 69.99%, 70%, 89.99%, 90%, 99.99%, and 100%+.

**Exit checks:** budget calculations match the specification and duplicate budgets are rejected consistently.

### Phase 5 - Dashboard and Insights

- Implement summary endpoint for income, expenses, balance, and savings rate.
- Return `N/A` savings rate when income is zero.
- Implement category breakdown, monthly trend, and budget-status endpoints.
- Add month selection with current calendar month as the default.
- Build responsive dashboard cards, donut chart, trend chart, and budget status view.
- Provide empty states for users with no transactions.

**Exit checks:** dashboard values are produced by backend calculations and match independently verified test fixtures.

### Phase 6 - Frontend Completion and Accessibility

- Add login, registration, dashboard, transactions, budgets, and settings routes.
- Add loading, empty, validation, unauthorized, conflict, and server-error states.
- Ensure keyboard navigation, semantic controls, labels, focus states, responsive layouts down to approximately 320px, and accessible chart summaries.
- Keep API calls in a typed service layer and avoid duplicating financial logic in React components.

**Exit checks:** primary user journeys work on desktop, tablet, and mobile viewport sizes.

### Phase 7 - Verification and Documentation

- Run unit, integration, API, frontend, and end-to-end tests.
- Add API documentation examples and local setup instructions to README.
- Create `VIVA.md` with ELI5 and technical explanations for architecture, database, authentication, security, financial logic, testing, deployment, trade-offs, limitations, and future work.
- Add structured request logging without passwords, tokens, or financial credentials.
- Add a production-safe health check and error handling that hides stack traces.

**Exit checks:** all required tests pass, documentation matches behavior, and no secrets appear in source or logs.

### Phase 8 - Deployment

- Provision managed PostgreSQL.
- Deploy backend and frontend separately.
- Configure production environment variables, CORS, HTTPS, cookie settings, migrations, and logging.
- Verify registration, login, transaction creation, budgets, dashboard calculations, logout, and data isolation against the deployed environment.

**Exit checks:** the MVP is publicly accessible and the smoke-test report is recorded.

## 6. API Contract Checklist

Base path: `/api/v1`

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET|POST /transactions`
- `GET|PATCH|DELETE /transactions/{id}`
- `GET|POST /budgets`
- `GET|PATCH|DELETE /budgets/{id}`
- `GET /dashboard/summary`
- `GET /dashboard/category-breakdown`
- `GET /dashboard/monthly-trend`
- `GET /dashboard/budget-status`

Use the consistent error shape from the spec:

```json
{
  "error": {
    "code": "INVALID_AMOUNT",
    "message": "Transaction amount must be greater than zero."
  }
}
```

Document query parameters, response schemas, authentication requirements, and status codes for every endpoint before frontend integration.

## 7. Test Matrix

### Unit tests

- Balance calculation.
- Savings rate, including zero income.
- Budget remaining and utilization.
- Threshold classification boundaries.
- Amount, date, description, and category validation.

### Integration and API tests

- Registration and authentication lifecycle.
- Protected endpoint behavior.
- Transaction CRUD, filters, search, sort, and pagination.
- Budget CRUD and uniqueness conflict.
- User A cannot read or modify User B's transactions, budgets, summaries, or alerts.
- Consistent error responses and status codes.

### Frontend and end-to-end tests

- Register, login, logout.
- Add, edit, delete, search, and filter transactions.
- Create and inspect budgets.
- Select dashboard month and verify displayed summaries.
- Empty, validation, loading, and error states.
- Responsive primary flows.

## 8. MVP Exit Criteria

The MVP is ready only when all required checklist items in `SPEC.md` are implemented, tested, documented, and smoke-tested in the deployed environment. Optional features such as custom categories, recurring transactions, CSV import/export, dark mode, and AI insights remain deferred until this gate passes.

## 9. Known Risks and Mitigations

- **Money precision:** use `Decimal` end-to-end and database numeric columns; never use binary floating point for persisted or aggregate financial values.
- **Data leakage:** scope every repository query by authenticated user id and test cross-user access explicitly.
- **Session theft:** use secure, HTTP-only, same-site cookies, short expiry, revocation on logout, and HTTPS in production.
- **Timezone errors:** store timestamps in UTC and centralize month/date interpretation using the configured application timezone.
- **Budget race conditions:** rely on the database uniqueness constraint and map conflicts to a stable `409` response.
- **Dashboard drift:** calculate summaries in backend services and cover them with fixture-based tests.

## 10. Immediate Next Task

The local implementation is complete through Phases 0-7. The remaining Phase 8 work requires external infrastructure: provision PostgreSQL, configure production secrets and HTTPS, deploy the backend and frontend containers, run `alembic upgrade head`, and execute the deployed smoke-test checklist. Docker is not installed in the current environment, so container execution and public deployment have not been claimed as verified.

## 11. Local Completion Record

- Phase 0: project setup, environment template, health endpoint, linting, and tests.
- Phase 1: SQLAlchemy models, Alembic migration, constraints, indexes, and seeded categories.
- Phase 2: Argon2id authentication, revocable HTTP-only sessions, protected identity endpoint, and auth tests.
- Phase 3: transaction CRUD, ownership isolation, filtering, search, sorting, pagination, and UI.
- Phase 4: budget CRUD, Decimal utilization, threshold classification, tests, and UI.
- Phase 5: backend dashboard aggregations, charts, month selection, and zero-income handling.
- Phase 6: responsive navigation, login, registration, settings/logout, loading/error/empty states, and accessible form labels.
- Phase 7: README, VIVA.md, CI workflow, structured API error envelope, and container definitions.

Local verification result: backend tests pass, Ruff passes, frontend lint passes, and the Next.js production build passes. The existing Starlette/httpx deprecation warning is non-blocking.
