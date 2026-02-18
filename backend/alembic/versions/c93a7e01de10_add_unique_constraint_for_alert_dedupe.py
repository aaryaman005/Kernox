"""add unique constraint for alert dedupe

Revision ID: c93a7e01de10
Revises: fb9c76a88195
Create Date: 2026-02-18 23:15:13.987142
"""

from typing import Sequence, Union
from alembic import op


# revision identifiers
revision: str = "c93a7e01de10"
down_revision: Union[str, Sequence[str], None] = "fb9c76a88195"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_alert_rule_endpoint_last_event",
        "alerts",
        ["rule_name", "endpoint_id", "last_event_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_alert_rule_endpoint_last_event",
        "alerts",
        type_="unique",
    )
