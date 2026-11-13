"""Create customers, responses and alerts.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa

from alembic import op

# Alembic uses these ids to know the ORDER of migrations.
revision = "0001"
down_revision = None  # this is the first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration: create the three tables (run by `alembic upgrade head`)."""
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), unique=True),  # optional, but never duplicated
        sa.Column("phone", sa.String(32), unique=True),
        sa.Column("kind", sa.String(16), nullable=False),  # buyer / painter
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "responses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("product_rating", sa.Integer, nullable=False),
        sa.Column("care_rating", sa.Integer, nullable=False),
        sa.Column("happy_rating", sa.Integer, nullable=False),
        sa.Column("mean", sa.Numeric(4, 2), nullable=False),
        sa.Column("category", sa.String(12), nullable=False),
        sa.Column("source", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        # The database itself refuses ratings outside 1-5.
        sa.CheckConstraint("product_rating BETWEEN 1 AND 5", name="ck_product_rating"),
        sa.CheckConstraint("care_rating BETWEEN 1 AND 5", name="ck_care_rating"),
        sa.CheckConstraint("happy_rating BETWEEN 1 AND 5", name="ck_happy_rating"),
    )
    # Indexes make the dashboard's filters and GROUP BY queries fast.
    op.create_index("ix_responses_customer_id", "responses", ["customer_id"])
    op.create_index("ix_responses_category", "responses", ["category"])
    op.create_index("ix_responses_created_at", "responses", ["created_at"])
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        # unique: one alert per response
        sa.Column(
            "response_id", sa.Integer, sa.ForeignKey("responses.id"), nullable=False, unique=True
        ),
        sa.Column("is_read", sa.Boolean, nullable=False),
        sa.Column("email_sent", sa.Boolean, nullable=False),
        sa.Column("sms_sent", sa.Boolean, nullable=False),
        sa.Column("draft_reply", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Undo the migration (run by `alembic downgrade base`). Drops in reverse order."""
    op.drop_table("alerts")
    op.drop_index("ix_responses_created_at", "responses")
    op.drop_index("ix_responses_category", "responses")
    op.drop_index("ix_responses_customer_id", "responses")
    op.drop_table("responses")
    op.drop_table("customers")
