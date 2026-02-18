"""add composite detection index on events

Revision ID: b60595342cc8
Revises: bd9b7f96e557
Create Date: 2026-02-18 16:32:12.967533

"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b60595342cc8"
down_revision: Union[str, Sequence[str], None] = "bd9b7f96e557"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_events_detection_lookup",
        "events",
        ["flat_event_type", "flat_severity", "timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_events_detection_lookup",
        table_name="events",
    )
