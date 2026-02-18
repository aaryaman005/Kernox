"""add gin index on events.payload

Revision ID: bd9b7f96e557
Revises: 0e714f9bbe97
Create Date: 2026-02-18 16:26:31.212609
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "bd9b7f96e557"
down_revision: Union[str, Sequence[str], None] = "0e714f9bbe97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_payload_gin "
        "ON events USING GIN (payload)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_events_payload_gin")
