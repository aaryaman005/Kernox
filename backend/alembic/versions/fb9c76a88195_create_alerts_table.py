"""create alerts table

Revision ID: fb9c76a88195
Revises: b60595342cc8
Create Date: 2026-02-18 23:03:17.494105
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision: str = "fb9c76a88195"
down_revision: Union[str, Sequence[str], None] = "b60595342cc8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # JSONB for Postgres, JSON fallback handled at model level
    json_type = postgresql.JSONB(astext_type=sa.Text())

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_name", sa.String(length=100), nullable=False),
        sa.Column("endpoint_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.Column("first_event_id", sa.String(length=64), nullable=False),
        sa.Column("last_event_id", sa.String(length=64), nullable=False),
        sa.Column("linked_event_ids", json_type, nullable=False),
        sa.Column(
            "is_escalated", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["endpoint_id"],
            ["endpoints.id"],
            ondelete="RESTRICT",
        ),
    )

    # Indexes
    op.create_index("idx_alerts_endpoint_id", "alerts", ["endpoint_id"])
    op.create_index("idx_alerts_rule_name", "alerts", ["rule_name"])
    op.create_index("idx_alerts_created_at", "alerts", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_alerts_created_at", table_name="alerts")
    op.drop_index("idx_alerts_rule_name", table_name="alerts")
    op.drop_index("idx_alerts_endpoint_id", table_name="alerts")
    op.drop_table("alerts")
