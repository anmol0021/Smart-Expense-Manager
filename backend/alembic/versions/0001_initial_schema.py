"""Create the initial application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-28
"""

from uuid import UUID

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


INCOME_CATEGORIES = (
    ("00000000-0000-0000-0000-000000000001", "Salary"),
    ("00000000-0000-0000-0000-000000000002", "Freelance"),
    ("00000000-0000-0000-0000-000000000003", "Business"),
    ("00000000-0000-0000-0000-000000000004", "Investment"),
    ("00000000-0000-0000-0000-000000000005", "Scholarship"),
    ("00000000-0000-0000-0000-000000000006", "Other"),
)
EXPENSE_CATEGORIES = (
    ("00000000-0000-0000-0000-000000000101", "Food"),
    ("00000000-0000-0000-0000-000000000102", "Housing"),
    ("00000000-0000-0000-0000-000000000103", "Transportation"),
    ("00000000-0000-0000-0000-000000000104", "Shopping"),
    ("00000000-0000-0000-0000-000000000105", "Entertainment"),
    ("00000000-0000-0000-0000-000000000106", "Healthcare"),
    ("00000000-0000-0000-0000-000000000107", "Education"),
    ("00000000-0000-0000-0000-000000000108", "Utilities"),
    ("00000000-0000-0000-0000-000000000109", "Travel"),
    ("00000000-0000-0000-0000-000000000110", "Subscriptions"),
    ("00000000-0000-0000-0000-000000000111", "Other"),
)


def upgrade() -> None:
    category_type = sa.Enum("INCOME", "EXPENSE", name="categorytype")
    transaction_type = sa.Enum("INCOME", "EXPENSE", name="transactiontype")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("type", category_type, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("type", transaction_type, nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_user_date", "transactions", ["user_id", "transaction_date"])
    op.create_index("ix_transactions_user_category", "transactions", ["user_id", "category_id"])

    op.create_table(
        "budgets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "category_id", "month", name="uq_budgets_user_category_month"
        ),
    )
    op.create_index("ix_budgets_user_month", "budgets", ["user_id", "month"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_token_hash", "sessions", ["token_hash"], unique=True)

    categories = [
        {"id": UUID(category_id), "name": name, "type": "INCOME"}
        for category_id, name in INCOME_CATEGORIES
    ] + [
        {"id": UUID(category_id), "name": name, "type": "EXPENSE"}
        for category_id, name in EXPENSE_CATEGORIES
    ]
    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("id", sa.Uuid()),
            sa.column("name", sa.String()),
            sa.column("type", category_type),
        ),
        categories,
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_token_hash", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_budgets_user_month", table_name="budgets")
    op.drop_table("budgets")
    op.drop_index("ix_transactions_user_category", table_name="transactions")
    op.drop_index("ix_transactions_user_date", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    bind = op.get_bind()
    sa.Enum(name="transactiontype").drop(bind, checkfirst=True)
    sa.Enum(name="categorytype").drop(bind, checkfirst=True)
