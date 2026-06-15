"""add province dimension table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-10
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "provinces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(20), nullable=False),
        sa.Column("name_full", sa.String(30), nullable=False),
        sa.Column("pinyin", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(20), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("gaokao_reform_type", sa.String(10), nullable=False),
        sa.Column("new_gaokao_first_year", sa.Integer(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("valid_tracks", sa.JSON(), nullable=False),
        sa.Column("region", sa.String(20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_provinces_code"),
        sa.UniqueConstraint("name", name="uq_provinces_name"),
        sa.UniqueConstraint("slug", name="uq_provinces_slug"),
    )


def downgrade() -> None:
    op.drop_table("provinces")
