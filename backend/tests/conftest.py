import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/test")
os.environ.setdefault("SECRET_KEY", "test-only-secret")
