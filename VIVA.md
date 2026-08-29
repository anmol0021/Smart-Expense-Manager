# Viva Preparation

## Problem

The application gives an individual one reliable place to record income and expenses, set monthly category limits, and understand spending patterns.

## Architecture

The frontend is a Next.js App Router application. It calls a versioned FastAPI REST API. The API separates routing, services, schemas, and persistence models. PostgreSQL stores durable financial data, while Alembic manages schema changes.

### ELI5

The frontend is the notebook cover, the API is the librarian who checks every request, and PostgreSQL is the organized archive. The user can only open their own pages.

### Technical

The API layer handles HTTP and authentication dependencies, the service layer owns business rules and Decimal calculations, and SQLAlchemy models map normalized entities to PostgreSQL tables.

## Database

PostgreSQL was selected for relational integrity, transactions, constraints, indexing, and reliable numeric types. Users own transactions, budgets, and sessions. Categories are shared seeded reference data. A budget has one unique `(user_id, category_id, month)` combination.

### ELI5

A relational database is a set of connected, labeled tables. The labels prevent a transaction from pointing to a missing user or category.

### Technical

UUID primary keys, foreign keys, check constraints, numeric monetary columns, and indexes enforce the data model. `NUMERIC(12, 2)` and Python `Decimal` prevent binary floating-point money errors.

## Authentication and Security

Registration validates email and password policy, then hashes passwords with Argon2id. Login creates a random token; only its SHA-256 hash is stored in the sessions table. The raw token is sent in an HTTP-only, same-site cookie. Logout revokes the session and clears the cookie. Every protected query is scoped by the authenticated user id.

### ELI5

The server gives the browser a temporary key, but stores only a scrambled copy of that key. Each request must present the key before private records are opened.

### Technical

Session expiry and revocation are checked on every protected request. Production should enable secure cookies and HTTPS. Secrets come from environment variables and are excluded from Git.

## Financial Logic

- Balance = income minus expenses.
- Savings rate = balance divided by income times 100; zero income returns `null`, displayed as `N/A`.
- Budget utilization = spent divided by budget times 100.
- Status thresholds are Normal below 70%, Warning from 70%, Critical from 90%, and Exceeded from 100%.
- Aggregations are calculated by backend services and serialized as Decimal values.

## Testing

The backend tests cover health, schema constraints, authentication lifecycle, ownership-scoped transaction CRUD, filters, pagination limits, budget boundaries, utilization, dashboard totals, trend zero-filling, and zero-income handling. Frontend verification uses ESLint and a production Next.js build. CI runs both suites on every push and pull request.

## Deployment

Build the backend and frontend containers, provision PostgreSQL, configure environment variables, run `alembic upgrade head`, and deploy the services behind HTTPS. Set `CORS_ORIGINS` to the exact frontend origin and `COOKIE_SECURE=true` in production. The included `docker-compose.yml` supports local PostgreSQL and backend development; managed hosting can run the same images.

## Trade-offs

- Cookie sessions were selected over stateless JWTs so logout revocation is direct and server-controlled.
- Seeded global categories reduce MVP complexity; custom category management is deferred.
- Trend aggregation in Python is portable across PostgreSQL and SQLite tests; larger deployments may move this grouping into optimized SQL.
- The UI uses the backend as the source of truth and intentionally does not calculate financial totals.

## Limitations and Future Improvements

The MVP has no bank integration, multi-currency conversion, recurring transactions, CSV import/export, push notifications, or financial advice. Future work should add category retrieval and management APIs, persisted threshold alerts, richer end-to-end browser tests, rate limiting, password reset, audit logs, and production observability.
