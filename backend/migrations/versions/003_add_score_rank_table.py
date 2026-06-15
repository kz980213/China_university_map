"""add score_rank_tables (一分一段)

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-10
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "score_rank_tables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("province_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("track", sa.String(20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("cumulative_rank", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["province_id"], ["provinces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "province_id", "year", "track", "score",
            name="uq_score_rank_entry",
        ),
    )
    # 位次查询的核心索引：(province_id, year, track, cumulative_rank)
    op.create_index(
        "ix_score_rank_lookup",
        "score_rank_tables",
        ["province_id", "year", "track", "cumulative_rank"],
    )


def downgrade() -> None:
    op.drop_index("ix_score_rank_lookup", table_name="score_rank_tables")
    op.drop_table("score_rank_tables")
