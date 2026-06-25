"""add province_cutlines (省批次控制线)

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-25
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "province_cutlines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("province_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("track", sa.String(20), nullable=False),
        sa.Column("batch", sa.String(20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("import_batch", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["province_id"], ["provinces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "province_id", "year", "track", "batch",
            name="uq_province_cutline",
        ),
    )
    op.create_index(
        "ix_province_cutline_lookup",
        "province_cutlines",
        ["province_id", "year", "track"],
    )


def downgrade() -> None:
    op.drop_index("ix_province_cutline_lookup", table_name="province_cutlines")
    op.drop_table("province_cutlines")
