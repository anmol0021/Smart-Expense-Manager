# Deployment Guide

This project is a full-stack app with:
- Frontend: Next.js
- Backend: FastAPI
- Database: PostgreSQL

Because it has a Python API and database, it cannot be hosted as a pure static site on GitHub Pages. The correct production setup is:

- Frontend: Netlify
- Backend: Render
- Database: Neon or Supabase

---

## 1) Frontend on Netlify

### Import the project
1. Push the project to GitHub.
2. Go to Netlify and click "Add new site" > "Import an existing project".
3. Select the GitHub repo.

### Build settings
Use the following settings:
- Base directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `.next`
- Framework preset: Next.js

### Environment variables
Add:
- `NEXT_PUBLIC_API_URL=https://your-render-backend-url`

Example:
- `NEXT_PUBLIC_API_URL=https://smart-expense-manager-api.onrender.com`

---

## 2) Backend on Render

### Create the backend service
1. Go to Render.
2. Click "New" > "Web Service".
3. Connect the GitHub repo.
4. Choose the backend folder as the root for the service.

### Build settings
- Runtime: Python
- Build command: `pip install -r requirements.txt` or use the repo's Python packaging setup
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

### Environment variables
Add:
- `DATABASE_URL=<your-production-postgres-url>`
- `SECRET_KEY=<long-random-secret>`
- `SESSION_COOKIE_NAME=smart_expense_session`
- `COOKIE_SECURE=true`
- `CORS_ORIGINS=https://your-netlify-site.netlify.app`
- `APP_TIMEZONE=Asia/Kolkata`

### Important
If the app uses cookie-based auth, the backend must allow the frontend domain in CORS and the cookie must be set with HTTPS.

---

## 3) Database on Neon / Supabase

### Recommended
Use Neon for a quick Postgres setup.

Create a database and copy the connection string to `DATABASE_URL`.

You will also need to run the Alembic migrations once the production DB is ready.

---

## 4) Run the database migrations in production

After the backend is deployed, run:

```bash
alembic upgrade head
```

This creates the tables and seeded categories.

---

## 5) Test live flow
Once both services are live:
1. Open the Netlify frontend
2. Register a new user
3. Log in
4. Create an expense or income transaction
5. Refresh the page
6. Confirm the entry persists

---

## 6) Why not GitHub Pages

GitHub Pages only hosts static files. It cannot run:
- FastAPI
- PostgreSQL
- authenticated API sessions
- database-backed user data

That is why the backend must stay on Render or another app host, and the frontend should be on Netlify.

---

## 7) Best current recommendation

Use:
- Netlify for frontend
- Render for backend
- Neon for database

This is the most practical and reliable way to make the app live while keeping the current project structure.
