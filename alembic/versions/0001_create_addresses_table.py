from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "0001_create_addresses_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("addresses")

