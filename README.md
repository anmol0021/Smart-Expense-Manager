# Smart Expense & Budget Manager

A full-stack personal finance application for tracking income, expenses, budgets, and spending insights.

## Project Status

Phase 5 dashboard setup is complete. See [SPEC.md](SPEC.md) for requirements and [PLAN.md](PLAN.md) for the implementation roadmap.

## Local Development

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item ..\.env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

The API health check is available at `http://localhost:8000/health`.

The migration creates the users, categories, transactions, budgets, and sessions tables and seeds the predefined categories. PostgreSQL must be running and match the `DATABASE_URL` in `.env` before applying it.

Authentication is provided through `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/logout`, and `/api/v1/auth/me`. Login creates a secure HTTP-only session cookie; passwords are stored only as Argon2id hashes. The current local configuration uses non-secure cookies for HTTP development, while production must set `COOKIE_SECURE=true` behind HTTPS.

Transactions are available through `/api/v1/transactions` with ownership-scoped CRUD, date/type/category filters, case-insensitive description search, sorting, and pagination. Request validation rejects future dates, non-positive amounts, mismatched category types, descriptions longer than 255 characters, and page sizes above 100.

Budgets are available through `/api/v1/budgets` and calculate spent amount, remaining amount, utilization, and status (`NORMAL`, `WARNING`, `CRITICAL`, or `EXCEEDED`) on the backend. The frontend workflows are available at `/transactions` and `/budgets`.

Active categories are served by the authenticated `/api/v1/categories` endpoint; transaction and budget forms load them from the database rather than maintaining a separate category catalog.

The dashboard endpoints are available under `/api/v1/dashboard` for monthly summaries, category breakdowns, six-month expense trends, and budget status. The dashboard UI is available at `/dashboard`.

Login, registration, and logout screens are available at `/login`, `/register`, and `/settings`. The dashboard, transactions, and budgets pages are protected by the backend session API.

## Containers and Deployment

For local PostgreSQL and backend development:

```powershell
docker compose up --build db backend
docker compose exec backend alembic upgrade head
```

Build the frontend separately with `docker build -t smart-expense-frontend ./frontend`. In production, set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `APP_TIMEZONE`, and `COOKIE_SECURE=true`; deploy behind HTTPS and run migrations before serving traffic. See [VIVA.md](VIVA.md) for architecture, security, testing, and trade-offs.

### Frontend

```powershell
cd frontend
npm run dev
```

The frontend is available at `http://localhost:3000`.

## Testing

```powershell
cd backend
pytest
ruff check .

cd ..\frontend
npm run lint
```
