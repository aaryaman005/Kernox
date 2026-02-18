"""upgrade payload to jsonb

Revision ID: 0e714f9bbe97
Revises: 34da25a66eb6
Create Date: 2026-02-18

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0e714f9bbe97"
down_revision: Union[str, Sequence[str], None] = "34da25a66eb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only run for PostgreSQL
    op.alter_column(
        "events",
        "payload",
        type_=postgresql.JSONB(),
        postgresql_using="payload::jsonb",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "events",
        "payload",
        type_=postgresql.JSON(),
        postgresql_using="payload::json",
        existing_nullable=False,
    )
